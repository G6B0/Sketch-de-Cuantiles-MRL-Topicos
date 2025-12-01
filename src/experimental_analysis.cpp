#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <algorithm>
#include <cmath>
#include <iomanip>
#include "MRL_sketch.h"

struct ErrorStats {
    double max_error;
    double avg_error;
    double max_normalized_error;
    double avg_normalized_error;
    int total_queries;
};

// Calcula el rank real de un valor x de un vector 
int rank_real(const std::vector<int>& datos_ordenados, int x) {
    int count = 0;
    for (int val : datos_ordenados) {
        if (val <= x) count++;
        else break;
    }
    return count;
}

// Calcula el quantile real
int quantile_real(const std::vector<int>& datos_ordenados, double phi) {
    int r = static_cast<int>(std::floor(phi * datos_ordenados.size()));
    if (r >= datos_ordenados.size()) r = datos_ordenados.size() - 1;
    if (r < 0) r = 0;
    return datos_ordenados[r];
}

// Evalúa el error en consultas de rank
ErrorStats evaluar_rank(MRL_sketch& sketch, const std::vector<int>& flujo, 
                        const std::vector<int>& datos_ordenados, 
                        float epsilon, std::ofstream& results_file) {
    ErrorStats stats = {0, 0, 0, 0, 0};
    
    // Seleccionar valores para consultar
    std::vector<int> valores_consulta;
    
    // Tomar percentiles y algunos valores específicos
    for (double p = 0.0; p <= 1.0; p += 0.1) {
        int idx = static_cast<int>(p * (datos_ordenados.size() - 1));
        valores_consulta.push_back(datos_ordenados[idx]);
    }
    
    // Agregar min, max y algunos valores intermedios
    valores_consulta.push_back(datos_ordenados.front());
    valores_consulta.push_back(datos_ordenados.back());
    
    int n = datos_ordenados.size();
    double error_esperado = epsilon * n;
    
    results_file << "\n=== Evaluación de RANK ===\n";
    results_file << "Valor,Rank_Real,Rank_Estimado,Error_Absoluto,Error_Normalizado,Error_Esperado\n";
    
    for (int x : valores_consulta) {
        int rank_verdadero = rank_real(datos_ordenados, x);
        int rank_estimado = sketch.rank(x);
        
        int error_abs = std::abs(rank_estimado - rank_verdadero);
        double error_norm = static_cast<double>(error_abs) / n;
        
        stats.max_error = std::max(stats.max_error, static_cast<double>(error_abs));
        stats.avg_error += error_abs;
        stats.max_normalized_error = std::max(stats.max_normalized_error, error_norm);
        stats.avg_normalized_error += error_norm;
        stats.total_queries++;
        
        results_file << x << "," << rank_verdadero << "," << rank_estimado << "," 
                     << error_abs << "," << error_norm << "," << error_esperado << "\n";
    }
    
    stats.avg_error /= stats.total_queries;
    stats.avg_normalized_error /= stats.total_queries;
    
    results_file << "\nEstadísticas RANK:\n";
    results_file << "Error máximo absoluto: " << stats.max_error << "\n";
    results_file << "Error promedio absoluto: " << stats.avg_error << "\n";
    results_file << "Error máximo normalizado: " << stats.max_normalized_error << "\n";
    results_file << "Error promedio normalizado: " << stats.avg_normalized_error << "\n";
    results_file << "Error esperado (εn): " << error_esperado << "\n";
    results_file << "Epsilon: " << epsilon << "\n";
    
    return stats;
}

// Evalúa el error en consultas de quantile
ErrorStats evaluar_quantile(MRL_sketch& sketch, const std::vector<int>& flujo,
                            const std::vector<int>& datos_ordenados,
                            float epsilon, std::ofstream& results_file) {
    ErrorStats stats = {0, 0, 0, 0, 0};
    
    int n = datos_ordenados.size();
    double error_esperado = epsilon * n;
    
    results_file << "\n=== Evaluación de QUANTILE ===\n";
    results_file << "Phi,Rank_Teorico,Quantile_Real,Quantile_Estimado,Rank_Estimado,Error_Rank_Abs,Error_Rank_Norm,Error_Esperado\n";
    
    // Probar diferentes valores de phi
    for (double phi = 0.0; phi <= 1.0; phi += 0.05) {
        int rank_teorico = static_cast<int>(std::floor(phi * n));
        int quantile_verdadero = quantile_real(datos_ordenados, phi);
        int quantile_estimado = sketch.quantile(phi);
        
        // El error del quantile se mide en términos del rank del valor devuelto
        int rank_del_quantile_estimado = rank_real(datos_ordenados, quantile_estimado);
        
        int error_abs = std::abs(rank_del_quantile_estimado - rank_teorico);
        double error_norm = static_cast<double>(error_abs) / n;
        
        stats.max_error = std::max(stats.max_error, static_cast<double>(error_abs));
        stats.avg_error += error_abs;
        stats.max_normalized_error = std::max(stats.max_normalized_error, error_norm);
        stats.avg_normalized_error += error_norm;
        stats.total_queries++;
        
        results_file << phi << "," << rank_teorico << "," << quantile_verdadero << "," 
                     << quantile_estimado << "," << rank_del_quantile_estimado << ","
                     << error_abs << "," << error_norm << "," << error_esperado << "\n";
    }
    
    stats.avg_error /= stats.total_queries;
    stats.avg_normalized_error /= stats.total_queries;
    
    results_file << "\nEstadísticas QUANTILE:\n";
    results_file << "Error máximo absoluto (en rank): " << stats.max_error << "\n";
    results_file << "Error promedio absoluto (en rank): " << stats.avg_error << "\n";
    results_file << "Error máximo normalizado: " << stats.max_normalized_error << "\n";
    results_file << "Error promedio normalizado: " << stats.avg_normalized_error << "\n";
    results_file << "Error esperado (εn): " << error_esperado << "\n";
    results_file << "Epsilon: " << epsilon << "\n";
    
    return stats;
}

void procesar_dataset(const std::string& filename, float epsilon) {
    std::string filepath = "../data/" + filename;
    std::ifstream file(filepath);
    
    if (!file.is_open()) {
        std::cerr << "Error: no se pudo abrir " << filepath << "\n";
        return;
    }
    
    // Leer datos
    std::vector<int> flujo;
    int value;
    while (file >> value) {
        flujo.push_back(value);
    }
    file.close();
    
    int n = flujo.size();
    if (n == 0) {
        std::cerr << "Error: archivo vacío " << filename << "\n";
        return;
    }
    
    std::cout << "\n========================================\n";
    std::cout << "Procesando: " << filename << "\n";
    std::cout << "Epsilon: " << epsilon << "\n";
    std::cout << "n = " << n << " elementos\n";
    
    // Crear archivo de resultados
    std::string output_filename = "../results/" + filename.substr(0, filename.find('.')) + 
                                  "_epsilon_" + std::to_string(epsilon).substr(0, 4) + ".csv";
    std::ofstream results_file(output_filename);
    
    results_file << "Dataset: " << filename << "\n";
    results_file << "n: " << n << "\n";
    results_file << "epsilon: " << epsilon << "\n";
    
    // Crear datos ordenados para comparación
    std::vector<int> datos_ordenados = flujo;
    std::sort(datos_ordenados.begin(), datos_ordenados.end());
    
    // Crear e insertar en sketch
    MRL_sketch sketch(n, epsilon);
    for (int x : flujo) {
        sketch.insertar(x);
    }
    
    ErrorStats rank_stats = evaluar_rank(sketch, flujo, datos_ordenados, epsilon, results_file);
    ErrorStats quantile_stats = evaluar_quantile(sketch, flujo, datos_ordenados, epsilon, results_file);
    
    results_file.close();
    
    std::cout << "\n--- Resumen ---\n";
    std::cout << "RANK - Error máx normalizado: " << rank_stats.max_normalized_error 
              << " (límite: " << epsilon << ")\n";
    std::cout << "RANK - Error prom normalizado: " << rank_stats.avg_normalized_error << "\n";
    std::cout << "QUANTILE - Error máx normalizado: " << quantile_stats.max_normalized_error 
              << " (límite: " << epsilon << ")\n";
    std::cout << "QUANTILE - Error prom normalizado: " << quantile_stats.avg_normalized_error << "\n";
    std::cout << "Resultados guardados \n";
}

int main() {
    // Crear directorio de resultados si no existe
    system("mkdir -p ../results");
    
    std::vector<std::string> datasets = {
        "chicago2015.txt",
        "chicago2016.txt",
        "Uniform.txt",
        "Log-normal.txt"
    };
    
    std::vector<float> epsilons = {0.1f, 0.05f};

    // Procesar cada combinación dataset-epsilon
    for (const std::string& dataset : datasets) {
        for (float eps : epsilons) {
            procesar_dataset(dataset, eps);
        }
    }
    
    return 0;
}
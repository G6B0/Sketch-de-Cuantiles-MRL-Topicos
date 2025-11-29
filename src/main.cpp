#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include "MRL_sketch.h"

int main() {

    float e;
    std::string filename;

    std::cout << "Ingrese el error soportado (epsilon): ";
    std::cin >> e;

    std::cout << "Ingrese el nombre del archivo dentro de data/: ";
    std::cin >> filename;

    // Construir ruta completa
    std::string filepath = "../data/" + filename;

    std::ifstream file(filepath);
    if (!file.is_open()) {
        std::cerr << "Error: no se pudo abrir el archivo " << filepath << "\n";
        return 1;
    }

    // Leer flujo
    std::vector<int> flujo;
    int value;
    while (file >> value) {
        flujo.push_back(value);
    }
    file.close();

    int n = flujo.size();
    if (n == 0) {
        std::cerr << "Error: el archivo está vacío.\n";
        return 1;
    }

    std::cout << "Se leyeron " << n << " datos desde " << filename << "\n";

    // Crear sketch
    MRL_sketch MRL(n, e);

    // Insertar flujo
    for (int x : flujo) {
        MRL.insertar(x);
    }

    std::cout << "Inserción completada.\n";

    // Menu
    int opcion;
    while (true) {
        std::cout << "\nMenu de consultas:\n";
        std::cout << "1. rank(x)\n";
        std::cout << "2. select(r)\n";
        std::cout << "3. Salir\n";
        std::cout << "Elija una opcion: ";
        std::cin >> opcion;

        if (opcion == 1) {
            int x;
            std::cout << "Ingrese x: ";
            std::cin >> x;
            std::cout << "rank(" << x << ") = " << MRL.rank(x) << "\n";
        }
        else if (opcion == 2) {
            int r;
            std::cout << "Ingrese r: ";
            std::cin >> r;
            std::cout << "select(" << r << ") = " << MRL.select(r) << "\n";
        }
        else if (opcion == 3) {
            break;
        }
        else {
            std::cout << "Opcion invalida.\n";
        }
    }

    return 0;
}

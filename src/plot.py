import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import glob
from io import StringIO

# Configuración de estilo
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10

def parse_results_file(filename):
    """Lee un archivo de resultados y extrae las secciones de rank y quantile"""
    with open(filename, 'r') as f:
        content = f.read()
    
    # Buscar metadata
    lines = content.split('\n')
    dataset_name = lines[0].split(':')[1].strip()
    n = int(lines[1].split(':')[1].strip())
    epsilon = float(lines[2].split(':')[1].strip())
    
    # Extraer sección de RANK
    rank_section = content.split('=== Evaluación de RANK ===')[1].split('=== Evaluación de QUANTILE ===')[0]
    rank_lines = [line for line in rank_section.strip().split('\n') if line.strip() and not line.startswith('Estadísticas')]
    rank_df = pd.read_csv(StringIO('\n'.join(rank_lines)))
    
    # Extraer sección de QUANTILE
    quantile_section = content.split('=== Evaluación de QUANTILE ===')[1].split('\n\nEstadísticas')[0]
    quantile_lines = [line for line in quantile_section.strip().split('\n') if line.strip()]
    quantile_df = pd.read_csv(StringIO('\n'.join(quantile_lines)))
    
    return {
        'dataset': dataset_name,
        'n': n,
        'epsilon': epsilon,
        'rank_df': rank_df,
        'quantile_df': quantile_df
    }

def create_summary_table(all_results, output_dir='../plots'):
    """GRÁFICO 1: Tabla resumen con todos los resultados"""
    os.makedirs(output_dir, exist_ok=True)
    
    summary_data = []
    
    for result in all_results:
        dataset = result['dataset'].replace('.txt', '')
        eps = result['epsilon']
        n = result['n']
        
        rank_df = result['rank_df']
        quant_df = result['quantile_df']
        
        summary_data.append({
            'Dataset': dataset,
            'ε': eps,
            'RANK Max': f"{rank_df['Error_Normalizado'].max():.4f}",
            'RANK Avg': f"{rank_df['Error_Normalizado'].mean():.4f}",
            'QUANTILE Max': f"{quant_df['Error_Rank_Norm'].max():.4f}",
            'QUANTILE Avg': f"{quant_df['Error_Rank_Norm'].mean():.4f}",
            'Cumple': '✓' if rank_df['Error_Normalizado'].max() <= eps and quant_df['Error_Rank_Norm'].max() <= eps else '✗'
        })
    
    summary_df = pd.DataFrame(summary_data)
    
    # Guardar como CSV
    summary_df.to_csv(f'{output_dir}/tabla_resumen.csv', index=False)
    
    # Crear visualización
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.axis('tight')
    ax.axis('off')
    
    table = ax.table(cellText=summary_df.values,
                     colLabels=summary_df.columns,
                     cellLoc='center',
                     loc='center',
                     bbox=[0, 0, 1, 1])
    
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2.5)
    
    # Colorear headers
    for i in range(len(summary_df.columns)):
        table[(0, i)].set_facecolor('#4472C4')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    # Colorear filas según cumplimiento
    for i in range(1, len(summary_df) + 1):
        cumple = summary_df.iloc[i-1]['Cumple']
        color = '#90EE90' if cumple == '✓' else '#FFB6C1'
        for j in range(len(summary_df.columns)):
            table[(i, j)].set_facecolor(color)
    
    plt.title('Resumen de Resultados Experimentales - Sketch MRL', fontsize=14, fontweight='bold', pad=20)
    plt.savefig(f'{output_dir}/1_tabla_resumen.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(summary_df.to_string(index=False))

def plot_error_comparison(all_results, output_dir='../plots'):
    """GRÁFICO 2: Comparación de errores máximos entre datasets"""
    os.makedirs(output_dir, exist_ok=True)
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle('Comparación de Errores Máximos por Dataset', fontsize=14, fontweight='bold')
    
    # Preparar datos
    datasets = []
    rank_errors_01 = []
    rank_errors_005 = []
    quant_errors_01 = []
    quant_errors_005 = []
    
    # Agrupar por dataset
    dataset_names = list(set([r['dataset'].replace('.txt', '') for r in all_results]))
    dataset_names.sort()
    
    for dataset in dataset_names:
        datasets.append(dataset)
        
        # Buscar resultados con ε=0.1
        result_01 = next((r for r in all_results if dataset in r['dataset'] and r['epsilon'] == 0.1), None)
        if result_01:
            rank_errors_01.append(result_01['rank_df']['Error_Normalizado'].max())
            quant_errors_01.append(result_01['quantile_df']['Error_Rank_Norm'].max())
        else:
            rank_errors_01.append(0)
            quant_errors_01.append(0)
        
        # Buscar resultados con ε=0.05
        result_005 = next((r for r in all_results if dataset in r['dataset'] and r['epsilon'] == 0.05), None)
        if result_005:
            rank_errors_005.append(result_005['rank_df']['Error_Normalizado'].max())
            quant_errors_005.append(result_005['quantile_df']['Error_Rank_Norm'].max())
        else:
            rank_errors_005.append(0)
            quant_errors_005.append(0)
    
    x = np.arange(len(datasets))
    width = 0.35
    
    # Gráfico RANK
    axes[0].bar(x - width/2, rank_errors_01, width, label='ε=0.1', alpha=0.8, color='#1f77b4')
    axes[0].bar(x + width/2, rank_errors_005, width, label='ε=0.05', alpha=0.8, color='#ff7f0e')
    axes[0].axhline(y=0.1, color='blue', linestyle='--', linewidth=1, alpha=0.5, label='Límite ε=0.1')
    axes[0].axhline(y=0.05, color='orange', linestyle='--', linewidth=1, alpha=0.5, label='Límite ε=0.05')
    axes[0].set_xlabel('Dataset')
    axes[0].set_ylabel('Error Normalizado Máximo')
    axes[0].set_title('Errores RANK')
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(datasets, rotation=45, ha='right')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3, axis='y')
    
    # Gráfico QUANTILE
    axes[1].bar(x - width/2, quant_errors_01, width, label='ε=0.1', alpha=0.8, color='#1f77b4')
    axes[1].bar(x + width/2, quant_errors_005, width, label='ε=0.05', alpha=0.8, color='#ff7f0e')
    axes[1].axhline(y=0.1, color='blue', linestyle='--', linewidth=1, alpha=0.5, label='Límite ε=0.1')
    axes[1].axhline(y=0.05, color='orange', linestyle='--', linewidth=1, alpha=0.5, label='Límite ε=0.05')
    axes[1].set_xlabel('Dataset')
    axes[1].set_ylabel('Error Normalizado Máximo')
    axes[1].set_title('Errores QUANTILE')
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(datasets, rotation=45, ha='right')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/2_comparacion_errores.png', dpi=300, bbox_inches='tight')
    plt.close()

def main():
    
    # Buscar archivos de resultados
    result_files = glob.glob('../results/*.csv')
    
    if not result_files:
        print("\n error: No se encontraron archivos de resultados en ../results/")
        print("Ejecute primero: ./experimental")
        return
    all_results = []
    
    # Procesar cada archivo
    for filename in result_files:
        print(f"Leyendo: {filename}")
        result = parse_results_file(filename)
        all_results.append(result)
    
    # Generar los 3 gráficos esenciales
    create_summary_table(all_results)
    plot_error_comparison(all_results)
    
    print("\nGráficos generados en ../plots/:")
if __name__ == "__main__":
    main()
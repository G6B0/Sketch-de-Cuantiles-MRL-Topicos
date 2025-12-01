import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import glob

# Configuración de estilo
plt.style.use('seaborn-v0_8-darkgrid')
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10

def parse_results_file(filename):
    """Lee un archivo de resultados y extrae las secciones de rank y quantile"""
    with open(filename, 'r') as f:
        content = f.read()
    
    # Buscar la sección de RANK
    rank_section = content.split('=== Evaluación de RANK ===')[1].split('=== Evaluación de QUANTILE ===')[0]
    rank_lines = [line for line in rank_section.strip().split('\n') if line.strip() and not line.startswith('Estadísticas')]
    
    # Buscar metadata del inicio
    lines = content.split('\n')
    dataset_name = lines[0].split(':')[1].strip()
    n = int(lines[1].split(':')[1].strip())
    epsilon = float(lines[2].split(':')[1].strip())
    
    # Leer datos de rank
    from io import StringIO
    rank_df = pd.read_csv(StringIO('\n'.join(rank_lines)))
    
    # Similar para quantile...
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

def plot_rank_errors(results_dict, output_dir='../plots'):
    """Genera gráficos de error de rank"""
    os.makedirs(output_dir, exist_ok=True)
    
    dataset = results_dict['dataset'].replace('.txt', '')
    epsilon = results_dict['epsilon']
    n = results_dict['n']
    df = results_dict['rank_df']
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(f'Análisis de Error RANK - {dataset} (ε={epsilon}, n={n})', fontsize=14, fontweight='bold')
    
    # 1. Error absoluto vs valor
    axes[0, 0].scatter(df['Valor'], df['Error_Absoluto'], alpha=0.6, s=50)
    axes[0, 0].axhline(y=epsilon*n, color='r', linestyle='--', label=f'Error esperado (εn={epsilon*n:.1f})')
    axes[0, 0].set_xlabel('Valor consultado')
    axes[0, 0].set_ylabel('Error absoluto')
    axes[0, 0].set_title('Error Absoluto por Valor')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # 2. Error normalizado vs valor
    axes[0, 1].scatter(df['Valor'], df['Error_Normalizado'], alpha=0.6, s=50, color='orange')
    axes[0, 1].axhline(y=epsilon, color='r', linestyle='--', label=f'Límite teórico (ε={epsilon})')
    axes[0, 1].set_xlabel('Valor consultado')
    axes[0, 1].set_ylabel('Error normalizado')
    axes[0, 1].set_title('Error Normalizado por Valor')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    # 3. Rank real vs estimado
    axes[1, 0].scatter(df['Rank_Real'], df['Rank_Estimado'], alpha=0.6, s=50, color='green')
    min_rank = min(df['Rank_Real'].min(), df['Rank_Estimado'].min())
    max_rank = max(df['Rank_Real'].max(), df['Rank_Estimado'].max())
    axes[1, 0].plot([min_rank, max_rank], [min_rank, max_rank], 'r--', label='Ideal (x=y)')
    axes[1, 0].set_xlabel('Rank Real')
    axes[1, 0].set_ylabel('Rank Estimado')
    axes[1, 0].set_title('Rank Estimado vs Real')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)
    
    # 4. Histograma de errores
    axes[1, 1].hist(df['Error_Normalizado'], bins=20, alpha=0.7, color='purple', edgecolor='black')
    axes[1, 1].axvline(x=epsilon, color='r', linestyle='--', linewidth=2, label=f'ε={epsilon}')
    axes[1, 1].axvline(x=df['Error_Normalizado'].mean(), color='g', linestyle='--', linewidth=2, 
                       label=f'Promedio={df["Error_Normalizado"].mean():.4f}')
    axes[1, 1].set_xlabel('Error Normalizado')
    axes[1, 1].set_ylabel('Frecuencia')
    axes[1, 1].set_title('Distribución de Errores Normalizados')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/rank_{dataset}_eps{epsilon}.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f'Gráfico guardado: rank_{dataset}_eps{epsilon}.png')

def plot_quantile_errors(results_dict, output_dir='../plots'):
    """Genera gráficos de error de quantile"""
    os.makedirs(output_dir, exist_ok=True)
    
    dataset = results_dict['dataset'].replace('.txt', '')
    epsilon = results_dict['epsilon']
    n = results_dict['n']
    df = results_dict['quantile_df']
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(f'Análisis de Error QUANTILE - {dataset} (ε={epsilon}, n={n})', fontsize=14, fontweight='bold')
    
    # 1. Error normalizado vs phi
    axes[0, 0].scatter(df['Phi'], df['Error_Rank_Norm'], alpha=0.6, s=50)
    axes[0, 0].axhline(y=epsilon, color='r', linestyle='--', label=f'Límite teórico (ε={epsilon})')
    axes[0, 0].set_xlabel('φ (percentil)')
    axes[0, 0].set_ylabel('Error normalizado en rank')
    axes[0, 0].set_title('Error Normalizado por Percentil')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # 2. Error absoluto vs phi
    axes[0, 1].scatter(df['Phi'], df['Error_Rank_Abs'], alpha=0.6, s=50, color='orange')
    axes[0, 1].axhline(y=epsilon*n, color='r', linestyle='--', label=f'Error esperado (εn={epsilon*n:.1f})')
    axes[0, 1].set_xlabel('φ (percentil)')
    axes[0, 1].set_ylabel('Error absoluto en rank')
    axes[0, 1].set_title('Error Absoluto por Percentil')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    # 3. Quantile real vs estimado
    axes[1, 0].scatter(df['Quantile_Real'], df['Quantile_Estimado'], alpha=0.6, s=50, color='green')
    min_q = min(df['Quantile_Real'].min(), df['Quantile_Estimado'].min())
    max_q = max(df['Quantile_Real'].max(), df['Quantile_Estimado'].max())
    axes[1, 0].plot([min_q, max_q], [min_q, max_q], 'r--', label='Ideal (x=y)')
    axes[1, 0].set_xlabel('Quantile Real')
    axes[1, 0].set_ylabel('Quantile Estimado')
    axes[1, 0].set_title('Quantile Estimado vs Real')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)
    
    # 4. Histograma de errores
    axes[1, 1].hist(df['Error_Rank_Norm'], bins=20, alpha=0.7, color='purple', edgecolor='black')
    axes[1, 1].axvline(x=epsilon, color='r', linestyle='--', linewidth=2, label=f'ε={epsilon}')
    axes[1, 1].axvline(x=df['Error_Rank_Norm'].mean(), color='g', linestyle='--', linewidth=2,
                       label=f'Promedio={df["Error_Rank_Norm"].mean():.4f}')
    axes[1, 1].set_xlabel('Error Normalizado en Rank')
    axes[1, 1].set_ylabel('Frecuencia')
    axes[1, 1].set_title('Distribución de Errores Normalizados')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/quantile_{dataset}_eps{epsilon}.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f'Gráfico guardado: quantile_{dataset}_eps{epsilon}.png')

def create_summary_table(all_results, output_dir='../plots'):
    """Crea tabla resumen con todos los resultados"""
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
            'n': n,
            'ε': eps,
            'RANK Max Error Norm': rank_df['Error_Normalizado'].max(),
            'RANK Avg Error Norm': rank_df['Error_Normalizado'].mean(),
            'RANK Max Error Abs': rank_df['Error_Absoluto'].max(),
            'QUANTILE Max Error Norm': quant_df['Error_Rank_Norm'].max(),
            'QUANTILE Avg Error Norm': quant_df['Error_Rank_Norm'].mean(),
            'QUANTILE Max Error Abs': quant_df['Error_Rank_Abs'].max(),
            'Cumple Garantía RANK': '✓' if rank_df['Error_Normalizado'].max() <= eps else '✗',
            'Cumple Garantía QUANTILE': '✓' if quant_df['Error_Rank_Norm'].max() <= eps else '✗'
        })
    
    summary_df = pd.DataFrame(summary_data)
    
    # Guardar como CSV
    summary_df.to_csv(f'{output_dir}/summary_table.csv', index=False)
    
    # Crear visualización de la tabla
    fig, ax = plt.subplots(figsize=(16, 6))
    ax.axis('tight')
    ax.axis('off')
    
    table = ax.table(cellText=summary_df.values,
                     colLabels=summary_df.columns,
                     cellLoc='center',
                     loc='center',
                     bbox=[0, 0, 1, 1])
    
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1, 2)
    
    # Colorear headers
    for i in range(len(summary_df.columns)):
        table[(0, i)].set_facecolor('#4472C4')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    plt.savefig(f'{output_dir}/summary_table.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print('\nTabla resumen creada:')
    print(summary_df.to_string(index=False))
    print(f'\nGuardada en: {output_dir}/summary_table.csv y summary_table.png')

def plot_comparison_by_epsilon(all_results, output_dir='../plots'):
    """Compara resultados entre diferentes epsilons para cada dataset"""
    os.makedirs(output_dir, exist_ok=True)
    
    datasets = list(set([r['dataset'].replace('.txt', '') for r in all_results]))
    
    for dataset in datasets:
        dataset_results = [r for r in all_results if dataset in r['dataset']]
        
        if len(dataset_results) < 2:
            continue
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        fig.suptitle(f'Comparación por ε - {dataset}', fontsize=14, fontweight='bold')
        
        # RANK comparison
        for result in dataset_results:
            eps = result['epsilon']
            df = result['rank_df']
            axes[0].scatter(df['Valor'], df['Error_Normalizado'], alpha=0.6, label=f'ε={eps}', s=30)
        
        axes[0].set_xlabel('Valor')
        axes[0].set_ylabel('Error Normalizado')
        axes[0].set_title('Error RANK')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # QUANTILE comparison
        for result in dataset_results:
            eps = result['epsilon']
            df = result['quantile_df']
            axes[1].scatter(df['Phi'], df['Error_Rank_Norm'], alpha=0.6, label=f'ε={eps}', s=30)
        
        axes[1].set_xlabel('φ (percentil)')
        axes[1].set_ylabel('Error Normalizado')
        axes[1].set_title('Error QUANTILE')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/comparison_epsilon_{dataset}.png', dpi=300, bbox_inches='tight')
        plt.close()
        print(f'Comparación guardada: comparison_epsilon_{dataset}.png')

def plot_comparison_by_distribution(all_results, output_dir='../plots'):
    """Compara resultados entre diferentes distribuciones para un mismo epsilon"""
    os.makedirs(output_dir, exist_ok=True)
    
    epsilons = list(set([r['epsilon'] for r in all_results]))
    
    for eps in epsilons:
        eps_results = [r for r in all_results if r['epsilon'] == eps]
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        fig.suptitle(f'Comparación por Distribución - ε={eps}', fontsize=14, fontweight='bold')
        
        # Preparar datos para boxplot
        rank_errors = {}
        quantile_errors = {}
        
        for result in eps_results:
            dataset = result['dataset'].replace('.txt', '')
            rank_errors[dataset] = result['rank_df']['Error_Normalizado'].values
            quantile_errors[dataset] = result['quantile_df']['Error_Rank_Norm'].values
        
        # RANK boxplot
        axes[0].boxplot(rank_errors.values(), labels=rank_errors.keys())
        axes[0].axhline(y=eps, color='r', linestyle='--', label=f'Límite ε={eps}')
        axes[0].set_ylabel('Error Normalizado')
        axes[0].set_title('Distribución de Errores RANK')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3, axis='y')
        plt.setp(axes[0].xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # QUANTILE boxplot
        axes[1].boxplot(quantile_errors.values(), labels=quantile_errors.keys())
        axes[1].axhline(y=eps, color='r', linestyle='--', label=f'Límite ε={eps}')
        axes[1].set_ylabel('Error Normalizado')
        axes[1].set_title('Distribución de Errores QUANTILE')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3, axis='y')
        plt.setp(axes[1].xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/comparison_distributions_eps{eps}.png', dpi=300, bbox_inches='tight')
        plt.close()
        print(f'Comparación guardada: comparison_distributions_eps{eps}.png')

def main():
    print("="*60)
    print("GENERACIÓN DE GRÁFICOS Y ANÁLISIS")
    print("="*60)
    
    # Buscar archivos de resultados
    result_files = glob.glob('../results/*.csv')
    
    if not result_files:
        print("Error: No se encontraron archivos de resultados en ../results/")
        print("Ejecute primero el programa experimental_analysis")
        return
    
    print(f"\nEncontrados {len(result_files)} archivos de resultados\n")
    
    all_results = []
    
    # Procesar cada archivo
    for filename in result_files:
        print(f"Procesando: {filename}")
        result = parse_results_file(filename)
        all_results.append(result)
        
        # Generar gráficos individuales
        plot_rank_errors(result)
        plot_quantile_errors(result)
    
    print("\n" + "="*60)
    print("Generando gráficos comparativos...")
    print("="*60 + "\n")
    
    # Generar comparaciones
    create_summary_table(all_results)
    plot_comparison_by_epsilon(all_results)
    plot_comparison_by_distribution(all_results)
    
    print("\n" + "="*60)
    print("PROCESO COMPLETADO")
    print("="*60)
    print("\nTodos los gráficos han sido guardados en ../plots/")
    print("\nArchivos generados:")
    print("- Gráficos individuales: rank_*.png, quantile_*.png")
    print("- Comparaciones por ε: comparison_epsilon_*.png")
    print("- Comparaciones por distribución: comparison_distributions_*.png")
    print("- Tabla resumen: summary_table.csv y summary_table.png")

if __name__ == "__main__":
    main()
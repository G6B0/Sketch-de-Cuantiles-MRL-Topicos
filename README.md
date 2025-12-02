
Poseer al menos uno de los archivos "chicago2015.txt", "chicago2016.txt", "Uniform.txt" y/o "Log-normal.txt" en una carpeta "data"

g++ experimental_analysis.cpp MRL_sketch.cpp -o experimental -std=c++14 -O2

./experimental

python3 plot.py
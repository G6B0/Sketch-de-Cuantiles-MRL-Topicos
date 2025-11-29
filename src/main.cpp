#include <iostream>
#include "MRL_sketch.h"
#include <vector>

int main(int argc, char const *argv[])
{
    int n;
    float e;

    std::cout << "Ingrese el valor total de datos\n";
    std::cin >> n;

    std::cout << "Ingrese el error a soportar entre [0,1]\n";
    std::cin >> e;

    MRL_sketch MRL(n,e);
    std::cout << "Sketch inicializado con n = " << n << " y e = " << e <<std::endl;
    std::vector<int> prueba;
    for(int i = 0; i < n; i++){
        MRL.insertar(i);
    }

    std::cout << MRL.rank(10) << "\n";
    std::cout << MRL.quantile(0.5) << "\n";
    
    
    return 0;
}

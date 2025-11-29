#ifndef MRL_SKETCH
#define MRL_SKETCH
#include <utility>
#include <vector>

class MRL_sketch
{
private:
    /* data */
    int n; //Total de datos
    float e; //Error asociado al sketch
    int k; //se calcula con e
    int L; // se calcula con k
    std::vector<std::vector<int>> A; // vector de niveles
    std::vector<std::pair<int,int>> B;
public:
    MRL_sketch(int n,float e);

    void insertar(int i);
    int rank(int x);
    int select(int r);
};
#endif
#include <cmath>
#include "MRL_sketch.h"
#include <vector>
#include <algorithm>

MRL_sketch::MRL_sketch(int n, float e) : n(n), e(e){
    k = (1.0 / e) * (std::ceil(std::log2(e * n))) + 1;
    L = std::ceil(std::log2(n / k));
    A.resize(L+1);
    for (size_t i = 0; i <= L; i++)
    {
        A[i].reserve(k);
    }
}

void MRL_sketch::insertar(int i){
    A[0].emplace_back(i);
    int j = 0;
    while (A[j].size() == k)
    {
        std::sort(A[j].begin(), A[j].end());
        if (j+1 <= L){
            for (size_t u = 0; u < A[j].size()/2; u++)
                {
                    A[j+1].emplace_back(A[j][2*u+1]);
                }
        }

        A[j].clear();
        B.clear();
        j++;
    }
}

int MRL_sketch::rank(int x){
    int ans = 0;
    for (size_t j = 0; j < L; j++)
    {
        for (size_t z = 0; z < A[j].size(); z++)
        {
            if (A[j][z] < x){
                ans = ans + (1 << j);
            }
        }
    }
    return ans;
}

int MRL_sketch::select(int r){
    if(B.empty()){
        for (size_t j = 0; j <= L; j++){
            for (size_t z = 0; z < A[j].size(); z++){
                int valor = A[j][z];
                B.emplace_back(valor, 1 << j);
            }
        }     
    }
    std::sort(B.begin(), B.end(), [](const auto &a, const auto &b){
        return a.first < b.first;
    });
    int a = 0;
    int primero = -1;
    for (size_t t = 0; t < B.size(); t++)
    {
        a = a + B[t].second;
        if(a >= r){
            primero = B[t].first;
            break;
        } 
    }
    return primero;
}
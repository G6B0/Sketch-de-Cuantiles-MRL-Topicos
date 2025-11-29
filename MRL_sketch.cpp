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
        j++;
    }
}


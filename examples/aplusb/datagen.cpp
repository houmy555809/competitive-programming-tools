#include <bits/stdc++.h>
#include <chrono>
using namespace std;

int main() {
    chrono::milliseconds ms = chrono::duration_cast<chrono::milliseconds>(
        chrono::system_clock::now().time_since_epoch()
    );
    srand(ms.count());
    cout << rand() << " " << rand() << endl;
    return 0;
}

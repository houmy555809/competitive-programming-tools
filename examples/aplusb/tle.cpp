#include<bits/stdc++.h>
using namespace std;
unsigned int a, b, c;
int main(){
    //brute-force approach;
    cin >> a >> b;
    for(int i = 0; i < a; i++) c++;
    for(int i = 0; i < b; i++) c++;
    cout << c << endl;
    return 0;
}
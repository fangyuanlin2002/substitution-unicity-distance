#include <algorithm>
#include <array>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <random>
#include <vector>
using namespace std;using V=__uint128_t;
struct Alias{array<double,26>p;array<int,26>a;void init(const double*q){vector<int>small,large;for(int j=0;j<26;j++){p[j]=26*q[j];(p[j]<1?small:large).push_back(j);}while(!small.empty()&&!large.empty()){int s=small.back();small.pop_back();int l=large.back();large.pop_back();a[s]=l;p[l]-=1-p[s];(p[l]<1?small:large).push_back(l);}for(int j:small)p[j]=1;for(int j:large)p[j]=1;}int sample(mt19937_64&r){int j=uniform_int_distribution<int>(0,25)(r);double u=generate_canonical<double,53>(r);return u<p[j]?j:a[j];}};
struct Entry{V pattern,word;bool operator<(const Entry&o)const{return pattern<o.pattern||(pattern==o.pattern&&word<o.word);}};
int main(int argc,char**argv){if(argc!=6)return 2;int order=stoi(argv[2]),n=stoi(argv[3]);size_t M=stoull(argv[4]);unsigned long long seed=stoull(argv[5]);if(n>25)return 3;ifstream in(argv[1],ios::binary);vector<double>p(26+676+17576);in.read((char*)p.data(),p.size()*8);if(!in)return 4;array<Alias,703>tab;tab[0].init(p.data());for(int h=0;h<26;h++)tab[1+h].init(p.data()+26+26*h);for(int h=0;h<676;h++)tab[27+h].init(p.data()+26+676+26*h);double u[26];fill(u,u+26,1./26);Alias uniform;uniform.init(u);mt19937_64 rng(seed);vector<Entry>v;v.reserve(M);
for(size_t j=0;j<M;j++){array<int,26>map;map.fill(-1);int d=0,last=0,prev=0;V x=0,s=0;for(int t=0;t<n;t++){int c;if(order<0)c=uniform.sample(rng);else {int h=order==0||t==0?0:order==1||t==1?1+last:27+26*prev+last;c=tab[h].sample(rng);}x=(x<<5)|c;if(map[c]<0)map[c]=d++;s=(s<<5)|map[c];prev=last;last=c;}v.push_back({s,x});}
sort(v.begin(),v.end());size_t success=0,classes=0,distinct=0;long double duplicatepairs=0;
for(size_t i=0;i<M;){size_t j=i+1;while(j<M&&v[j].pattern==v[i].pattern)j++;classes++;if(v[i].word==v[j-1].word)success+=j-i;for(size_t k=i;k<j;){size_t l=k+1;while(l<j&&v[l].word==v[k].word)l++;distinct++;duplicatepairs+=(long double)(l-k)*(l-k-1)/2;k=l;}i=j;}
cout<<setprecision(15)<<order<<','<<n<<','<<M<<','<<seed<<','<<success/(double)M<<','<<classes/(double)M<<','<<distinct<<','<<(double)duplicatepairs<<'\n';return 0;}

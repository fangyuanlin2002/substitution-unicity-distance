#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <random>
#include <sstream>
#include <string>
#include <vector>
using namespace std; using U128=__uint128_t;
struct Record{U128 p,w;};
bool byword(const Record&a,const Record&b){return a.w<b.w;}
bool bypattern(const Record&a,const Record&b){return a.p<b.p || (a.p==b.p && a.w<b.w);}
Record encode(const uint8_t*x,int n){int seen[26]; fill(seen,seen+26,-1);int d=0;Record r{0,0};for(int i=0;i<n;++i){int a=x[i];if(seen[a]<0)seen[a]=d++;r.p=(r.p<<5)|seen[a];r.w=(r.w<<5)|a;}return r;}
int distinct(U128 p,int n){int m=0;for(int i=0;i<n;++i){m=max(m,int(p&31));p>>=5;}return m+1;}
struct Stats{double unique,map,entropy,key;size_t singleton,classes;};
Stats statistics(vector<Record>&r,int n,bool corpus){sort(r.begin(),r.end(),bypattern);size_t good=0,cl=0;double h=0,key=0;for(size_t i=0;i<r.size();){size_t j=i+1;while(j<r.size()&&r[j].p==r[i].p)++j;bool value_unique=(r[j-1].w==r[i].w);if(value_unique)good+=j-i;cl++;h+=(j-i)*log2(double(j-i));if(corpus)key+=(j-i)*lgamma(27-distinct(r[i].p,n))/log(2.);i=j;}return {double(good)/r.size(),double(cl)/r.size(),h/r.size(),key/r.size(),good,cl};}
vector<uint64_t> corpus(const string&root){vector<vector<uint8_t>> books;for(string name: {"alice","pride_and_prejudice","frankenstein","moby_dick","sherlock_holmes","huckleberry_finn"}){ifstream f(root+"/data/"+name+".txt");string s;getline(f,s);if(s.empty())throw runtime_error("missing book");vector<uint8_t>b;for(char c:s)b.push_back(c-'A');books.push_back(move(b));}ofstream out(root+"/data/census.csv");out<<"N,M,unique,map_success,plaintext_entropy,residual_key_bits,singletons,classes\n"<<setprecision(17);vector<uint64_t> Ms(25);for(int n=10;n<=24;n++){vector<Record> r;for(auto&b:books)for(size_t i=0;i+n<=b.size();i++)r.push_back(encode(b.data()+i,n));sort(r.begin(),r.end(),byword);r.erase(unique(r.begin(),r.end(),[](auto&a,auto&b){return a.w==b.w;}),r.end());Ms[n]=r.size();auto s=statistics(r,n,true);out<<n<<','<<r.size()<<','<<s.unique<<','<<s.map<<','<<s.entropy<<','<<s.key<<','<<s.singleton<<','<<s.classes<<'\n';out.flush();cerr<<"census "<<n<<" "<<r.size()<<" "<<s.unique<<'\n';}return Ms;}
struct Model{vector<array<double,26>> cdf[4];int fallback[4]={};Model(const string&root){string names[4]={"mono","bi","tri","quad"};for(int k=0;k<4;k++){size_t rows=1;for(int j=0;j<k;j++)rows*=26;cdf[k].resize(rows);ifstream f(root+"/sources/english_"+names[k]+"grams.txt");string s;double v;while(f>>s>>v){int row=0;for(int i=0;i<k;i++)row=row*26+s[i]-'A';cdf[k][row][s[k]-'A']=v;}for(size_t row=0;row<rows;row++){double sum=accumulate(cdf[k][row].begin(),cdf[k][row].end(),0.);if(sum==0){if(k==0)throw runtime_error("zero mono");fallback[k]++;cdf[k][row]=cdf[k-1][row%cdf[k-1].size()];continue;}double z=0;for(int a=0;a<26;a++){z+=cdf[k][row][a]/sum;cdf[k][row][a]=z;}cdf[k][row][25]=1;}}}
int draw(mt19937_64&rng,int order,const uint8_t*x,int t){int k=min(order,t),row=0;for(int j=t-k;j<t;j++)row=row*26+x[j];double u=(rng()>>11)*0x1.0p-53;auto&c=cdf[k][row];return upper_bound(c.begin(),c.end(),u)-c.begin();}};
vector<uint64_t> getMs(const string&root){ifstream f(root+"/data/census.csv");string s;getline(f,s);vector<uint64_t>M(25);while(getline(f,s)){stringstream q(s);string a,b;getline(q,a,',');getline(q,b,',');M[stoi(a)]=stoull(b);}return M;}
void simulate(string root,int order,int rep){auto M=getMs(root);uint64_t maxm=*max_element(M.begin(),M.end());if(maxm==0)throw runtime_error("missing census");Model model(root);uint64_t seed=202611190000ULL+order*100+rep;mt19937_64 rng(seed);vector<array<uint8_t,24>> words(maxm);for(auto&x:words)for(int t=0;t<24;t++)x[t]=model.draw(rng,order,x.data(),t);ofstream out(root+"/data/sim_Q"+to_string(order)+"_"+to_string(rep)+".csv");out<<"N,model,rep,unique,seed,M\n"<<setprecision(17);for(int n=10;n<=24;n++){vector<Record>r(M[n]);for(size_t j=0;j<M[n];j++)r[j]=encode(words[j].data(),n);auto s=statistics(r,n,false);out<<n<<",Q"<<order<<','<<rep<<','<<s.unique<<','<<seed<<','<<M[n]<<'\n';out.flush();cerr<<"sim Q"<<order<<" rep "<<rep<<" N "<<n<<" u "<<s.unique<<'\n';}for(int k=0;k<4;k++)cerr<<"fallback "<<k<<" "<<model.fallback[k]<<'\n';}
int main(int argc,char**argv){string root=argv[1];string mode=argv[2];if(mode=="census")corpus(root);else simulate(root,stoi(argv[3]),stoi(argv[4]));return 0;}

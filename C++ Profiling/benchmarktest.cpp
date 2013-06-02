
#include <iostream>
#include "benchmark.h"

Profile* Profile::m_instance = NULL;


void func(void)
{
    //Benchmark l_benchmark1("xx");
    for(std::size_t i=0; i < 100000; ++i)
        ;
}



int main(int p_argc, char* p_argv[])
{
    //Benchmark l_benchmark1("yy");
    func();
    //std::cout << *Profile::getInstance() << std::endl;
}

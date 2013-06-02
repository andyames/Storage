
#include <iostream>
#include "benchmark.h"


PROFILINGDEFINITION


void func(void)
{
    PROFILING
    for(std::size_t i=0; i < 100000; ++i)
        ;
}



int main(int p_argc, char* p_argv[])
{
    PROFILINGINIT
    
    PROFILING
    func();
    std::cout << PROFILINGINSTANCE << std::endl;
    
    PROFILINGCLOSE
}

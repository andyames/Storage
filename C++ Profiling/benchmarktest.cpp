
#include <iostream>
#include "benchmark.h"


PROFILINGDEFINITION


void func(void)
{
    PROFILING
    for(std::size_t i=0; i < 100000; ++i)
    {
        PROFILING_NAME("loop")
    }
}



int main(int p_argc, char* p_argv[])
{
    PROFILINGINIT
    
    func();
    func();
    func();
    
    std::cout << PROFILINGINSTANCE << std::endl;
    
    PROFILINGCLOSE
}

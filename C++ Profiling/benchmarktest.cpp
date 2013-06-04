
#include <iostream>
#include "benchmark.h"

PROFILINGINIT


void func(void)
{
    PROFILING
    for(std::size_t i=0; i < 100000; ++i)
    {
        PROFILINGNAME("loop")
    }
}



int main(int p_argc, char* p_argv[])
{
    func();
    func();
    func();
    
    PROFILINGCOUT
}

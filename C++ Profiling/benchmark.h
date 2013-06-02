#ifndef __BENCHMARK
#define __BENCHMARK

#include "profile.h"

#ifdef _WIN32
extern "C" {
#include <intrin.h>    
}
#endif


class Benchmark
{
    public :
    
        Benchmark( const std::string& p_functionname );
        ~Benchmark( void );
    
    
    private :
    
        const std::string m_functionname;
    
        unsigned long long m_starttime;
    
        unsigned long long m_endtime;
    
        static unsigned long long getCycles( void );
};

#endif

#include "profile.h"

#ifdef BENCHMARK

    #ifndef __BENCHMARK
    #define __BENCHMARK

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

        // http://linux.die.net/man/2/getrusage
        // http://stackoverflow.com/questions/63166/how-to-determine-cpu-and-memory-consumption-from-inside-a-process
        // http://www.gamasutra.com/view/feature/1430/monitoring_your_pcs_memory_usage_.php?print=1
        // http://nadeausoftware.com/articles/2012/07/c_c_tip_how_get_process_resident_set_size_physical_memory_use


        //http://stackoverflow.com/questions/9887839/clock-cycle-count-wth-gcc

        #ifdef _MSC_VER

            #ifdef _M_IX86
            inline unsigned long long Benchmark::getCycles(void)
            {
                unsigned long long c;
                __asm {
                    cpuid 
                    rdtsc  
                    mov dword ptr [c + 0], eax
                    mov dword ptr [c + 4], edx
                }
                return c;
            }

            #elif defined(_M_X64)
            extern "C" unsigned __int64 __rdtsc();
            #pragma intrinsic(__rdtsc)
            inline unsigned long long Benchmark::getCycles()
            {
                return __rdtsc();
            }
            #endif

        #endif


        #ifdef __GNUC__

            #ifdef __LP64__
            inline unsigned long long Benchmark::getCycles(void)
            {
                unsigned long long a, d;
                __asm__ volatile ("rdtsc" : "=a" (a), "=d" (d));
                return (d<<32) | a;
            }
            
            #else
            inline unsigned long long Benchmark::getCycles(void)
            {
                unsigned long long x;
                __asm__ volatile ("rdtsc" : "=A" (x));
                return x;
            }
            #endif

        #endif

    #endif

#endif

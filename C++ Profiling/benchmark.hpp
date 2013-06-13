#ifdef BENCHMARK

    #ifndef __BENCHMARK
    #define __BENCHMARK

        #include <boost/static_assert.hpp>

        #include "profile.hpp"

        #if (defined(__APPLE__) && defined(__MACH__))
            #include <mach/mach.h>
            #include <mach/mach_time.h>
        #elif defined(_MSC_VER) && defined(_M_X64)
            extern "C" unsigned __int64 __rdtsc();
        #endif


        template<typename T> class Benchmark
        {
            BOOST_STATIC_ASSERT( !boost::is_integral<T>::value );
            
            public :
            
                Benchmark( const std::string& p_functionname ) : m_functionname(p_functionname), m_starttime(getCycles()) {};
                ~Benchmark( void ) { unsigned long long l_endtime = getCycles(); Profile<T>::getInstance()->setBenchmarkTime( m_functionname, getCPUFrequencyScale() * (l_endtime-m_starttime) ); };
            
            
            private :
            
                const std::string m_functionname;
            
                unsigned long long m_starttime;
            

            
                // http://www.codeproject.com/Articles/184046/Spin-Lock-in-C
                
                // http://linux.die.net/man/2/getrusage
                // http://stackoverflow.com/questions/63166/how-to-determine-cpu-and-memory-consumption-from-inside-a-process
                // http://www.gamasutra.com/view/feature/1430/monitoring_your_pcs_memory_usage_.php?print=1
                // http://nadeausoftware.com/articles/2012/07/c_c_tip_how_get_process_resident_set_size_physical_memory_use
                // http://man7.org/linux/man-pages/man3/mallinfo.3.html
                // http://stackoverflow.com/questions/5120861/how-to-measure-memory-usage-from-inside-a-c-program
                // http://www.jimbrooks.org/web/c++/system_specific.php
                
                // http://www.codeproject.com/Articles/87529/Calculate-Memory-Working-Set-Private-Programmatica
                // http://www.codeproject.com/Articles/10520/Detecting-memory-leaks-by-using-CRT-diagnostic-fun
                // http://www.linuxtopia.org/online_books/programming_books/thinking_in_c++/Chapter13_016.html
                // http://www.gnu.org/software/libc/manual/html_node/Hooks-for-Malloc.html
                // http://stackoverflow.com/questions/929893/how-can-i-override-malloc-calloc-free-etc-under-os-x
                
                
                //http://stackoverflow.com/questions/9887839/clock-cycle-count-wth-gcc
                
                #if defined(_MSC_VER) && defined(_M_IX86)
                        
                    unsigned long long getCycles(void)
                    {
                        unsigned long long c;
                        __asm {
                            cpuid 
                            rdtsc  
                            mov dword ptr [c + 0], eax
                            mov dword ptr [c + 4], edx
                        }
                        return c;
                    };
                
                #elif defined(_MSC_VER) && defined(_M_X64)
                        
                    #pragma intrinsic(__rdtsc)
                    unsigned long long getCycles( void ) { return __rdtsc(); };
                
                #elif (defined(__unix__) || defined(__unix) || defined(unix)) && defined(__LP64__)
                
                    unsigned long long getCycles( void )
                    {
                        unsigned long long a, d;
                        __asm__ volatile ("rdtsc" : "=a" (a), "=d" (d));
                        return (d<<32) | a;
                    };
                
                #elif (defined(__unix__) || defined(__unix) || defined(unix)) && !defined(__LP64__)
                
                    unsigned long long getCycles( void )
                    {
                        unsigned long long x;
                        __asm__ volatile ("rdtsc" : "=A" (x));
                        return x;
                    };
                
                #elif defined(__APPLE__) && defined(__MACH__)
            
                    unsigned long long getCycles( void ) { return mach_absolute_time(); };
                
                #else 
                    #error "Unable to define getCycles( ) for an unknown OS."
                #endif

            
            
            
            
                static T getCPUFrequencyScale( void )
                {
                    // http://msdn.microsoft.com/en-us/library/windows/desktop/ms644905(v=vs.85).aspx
                    // http://developer.apple.com/library/mac/#qa/qa1398/_index.html  / http://www.macresearch.org/tutorial_performance_and_time 
                
                    T l_scale = 1;
                
                    #if defined(__APPLE__) && defined(__MACH__)
                        mach_timebase_info_data_t l_timeinfo;
                        if (!mach_timebase_info( &l_timeinfo ))
                            l_scale =  1e-6 * static_cast<double>(l_timeinfo.numer) / l_timeinfo.denom; 
                    #endif
                
                    return l_scale;
                };
            
        };

    #endif 

#endif

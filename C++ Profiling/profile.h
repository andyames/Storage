#ifndef BENCHMARK

    #define PROFILE

#else
    
    #ifndef __PROFILE
    #define __PROFILE
    
        //#define PROFILE   Benchmark l_benchmark__LINE__(__FUNCTION__);


        #include <map>
        #include <vector>
        #include <string>
        #include <numeric>
        #include <iostream>
        #include <stdexcept>
        #include <boost/thread.hpp>
        #include "benchmark.h"
        //#include <boost/shared_ptr.hpp>



        class Profile
        {
            public :
            
                static void createInstance( void );
                static void releaseInstance( void );
                static Profile* getInstance( void );
            
                std::map<std::string, std::vector<unsigned long long> > getTimes( void ) const;
                std::map<std::string, std::vector<unsigned long long> > getMemory( void ) const;
                void setBenchmarkTime( const std::string&, const unsigned long long& ); 
            
                //void setBenchmarkMemory( const std::string& p_name, ??? )
                //boost::shared_ptr<Benchmark> benchmark( const std::string& ) const;
                
            
                friend std::ostream& operator<< ( std::ostream&, const Profile& );

            
            
            
            private :
                
                Profile( void ) : m_muxtimes(), m_muxmemory(), m_times(), m_memory() {};
                ~Profile( void ); 
                Profile( const Profile& ) {};
                Profile& operator=( const Profile& );
            
                static void AverageDerivationMedian( const std::vector<unsigned long long>&, double&, double&, unsigned long long& );
                static unsigned long long getCycles( void );
            
                static Profile* m_instance;

                boost::mutex m_muxtimes;
                boost::mutex m_muxmemory;
                std::map< std::string, std::vector<unsigned long long> > m_times;
                std::map< std::string, std::vector<unsigned long long> > m_memory;
            
        };



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
            
            #ifdef __i386__
            inline unsigned long long Benchmark::getCycles(void)
            {
                unsigned long long x;
                __asm__ volatile ("rdtsc" : "=A" (x));
                return x;
            }
            
            #elif defined(__X86_64__)
            inline unsigned long long Benchmark::getCycles(void)
            {
                unsigned long long a, d;
                __asm__ volatile ("rdtsc" : "=a" (a), "=d" (d));
                return (d<<32) | a;
            }
            #endif

        #endif

    #endif

#endif

#ifndef BENCHMARK

    #define PROFILING
    #define PROFILINGNAME(name)

    #define PROFILINGINIT
    #define PROFILINGRELEASE
    #define PROFILINGDEFINITION
    #define PROFILINGSHOW

#else
    
    #ifndef __PROFILE
    #define __PROFILE
    
        #define PROFILING               Benchmark l_benchmark__LINE__(__PRETTY_FUNCTION__);
        #define PROFILINGNAME(name)     Benchmark l_benchmark__LINE__(name);

        #define PROFILINGINIT           Profile* Profile::m_instance = new Profile();
        #define PROFILINGCOUT           std::cout << *Profile::getInstance() << std::endl;


        #include <ios>
        #include <map>
        #include <string>
        #include <vector>
        #include <iomanip>
        #include <numeric>
        #include <sstream>
        #include <iostream>
        #include <stdexcept>
        #include <boost/bind.hpp>
        #include <boost/atomic.hpp>
        #include <boost/accumulators/accumulators.hpp>
        #include <boost/accumulators/statistics/sum.hpp>
        #include <boost/accumulators/statistics/min.hpp>
        #include <boost/accumulators/statistics/max.hpp>
        #include <boost/accumulators/statistics/mean.hpp>
        #include <boost/accumulators/statistics/stats.hpp>
        #include <boost/accumulators/statistics/count.hpp>
        #include <boost/accumulators/statistics/median.hpp>
        #include <boost/accumulators/statistics/variance.hpp>
        #include <boost/accumulators/statistics/extended_p_square.hpp>
        
        #include "benchmark.h"




        class Profile
        {
            public :
            
                typedef boost::accumulators::accumulator_set<double, boost::accumulators::stats< 
                    boost::accumulators::tag::count,
                    boost::accumulators::tag::sum,
                    boost::accumulators::tag::median, 
                    boost::accumulators::tag::mean, 
                    boost::accumulators::tag::variance,
                    boost::accumulators::tag::min,
                    boost::accumulators::tag::max
                    //boost::accumulators::tag::extended_p_square
                > > Accumulator;
            
            
                static void releaseInstance( void );
                static Profile* getInstance( void );
            
                static std::size_t getMemorySize(void);
                std::map< std::string, Accumulator > getTimes( void ) const { return m_times; }
            
                void setBenchmarkTime( const std::string&, const double& ); 
            
                friend std::ostream& operator<< ( std::ostream&, const Profile& );

            
            
            
            private :
            
                class Spinlock {
                  
                    public :
                    
                        Spinlock( void ) : m_state(Unlocked) {};
                        ~Spinlock( void ) { unlock(); };
                    
                        void lock( void )
                        {
                            while (m_state.exchange(Locked, boost::memory_order_relaxed) == Locked)
                                __asm__ __volatile__ ("rep; nop" : : );
                            atomic_thread_fence(boost::memory_order_acquire);     
                        };
                    
                        void unlock( void )
                        {
                            m_state.store(Unlocked, boost::memory_order_release);
                        };
                    
                    
                    private :
                    
                        typedef enum {Locked, Unlocked} LockState;
                        boost::atomic<LockState> m_state;
                    
                };
            
                
            
                static Profile* m_instance;

                Spinlock m_locktimes;
                std::map< std::string, Accumulator > m_times;
                std::map< std::string, Accumulator > m_memory;

            
                Profile( void ) : m_locktimes(), m_times(), m_memory() {};
                ~Profile( void ) {};
                Profile( const Profile& ) {};
                Profile& operator=( const Profile& );
                
                template<typename T> static std::string convert( const T&, const std::size_t& = 5 );
        };

        template<typename T> inline std::string Profile::convert( const T& p_in, const std::size_t& p )
        {
            std::ostringstream os;
            os << std::fixed << std::setprecision(p) << p_in;
            return os.str();
        }

    #endif

#endif

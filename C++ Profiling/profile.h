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
    
        #define PROFILING               Benchmark l_benchmark__LINE__(__FUNCTION__);
        #define PROFILINGNAME(name)     Benchmark l_benchmark__LINE__(name);

        #define PROFILINGINIT           Profile::createInstance();
        #define PROFILINGRELEASE        Profile::releaseInstance();
        #define PROFILINGDEFINITION     Profile* Profile::m_instance = NULL;
        #define PROFILINGSHOW           std::cout << *Profile::getInstance() << std::endl;


        #include <map>
        #include <string>
        #include <vector>
        #include <numeric>
        #include <sstream>
        #include <iostream>
        #include <stdexcept>
        #include <boost/bind.hpp>
        #include <boost/atomic.hpp>
        #include <boost/accumulators/accumulators.hpp>
        #include <boost/accumulators/statistics/min.hpp>
        #include <boost/accumulators/statistics/max.hpp>
        #include <boost/accumulators/statistics/mean.hpp>
        #include <boost/accumulators/statistics/stats.hpp>
        #include <boost/accumulators/statistics/median.hpp>
        #include <boost/accumulators/statistics/variance.hpp>

        #include "benchmark.h"


        class Profile
        {
            public :
            
                static void createInstance( void );
                static void releaseInstance( void );
                static Profile* getInstance( void );
            
                std::map<std::string, std::vector<unsigned long long> > getTimes( void ) const;
                std::map<std::string, std::vector<unsigned long long> > getMemory( void ) const;
                void setBenchmarkTime( const std::string&, const unsigned long long& ); 
                static std::size_t getMemorySize(void);
            
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
                std::map< std::string, std::vector<unsigned long long> > m_times;
                std::map< std::string, std::vector<unsigned long long> > m_memory;

            
                Profile( void ) : m_locktimes(), m_times(), m_memory() {};
                ~Profile( void ) {};
                Profile( const Profile& ) {};
                Profile& operator=( const Profile& );
                
                template<typename T> static std::string convert( const T& );
                template<typename T, typename L> static void AverageDerivationMedian( const std::vector<T>&, L&, L&, T&, T&, T& );
                static std::string repeat( const std::size_t&, const std::string& = " " );
            
        };


        template<typename T, typename L> inline void Profile::AverageDerivationMedian( const std::vector<T>& p_vec, L& p_average, L& p_stdderivation, T& p_median, T& p_min, T& p_max )
        {
            if (p_vec.empty())
            {
                p_stdderivation = p_average = static_cast<L>(0);
                p_median = static_cast<T>(0);
                return;
            }
            
            
            boost::accumulators::accumulator_set<T, 
                boost::accumulators::stats< 
                    boost::accumulators::tag::median, 
                    boost::accumulators::tag::mean, 
                    boost::accumulators::tag::variance,
                    boost::accumulators::tag::min,
                    boost::accumulators::tag::max
                >
            > l_acc;
            std::for_each( p_vec.begin(), p_vec.end(), boost::bind<void>( boost::ref(l_acc), _1 ));
            
            
            p_stdderivation = sqrt( boost::accumulators::variance(l_acc) );
            p_average       = boost::accumulators::mean(l_acc);
            p_median        = boost::accumulators::median(l_acc);
            p_min           = boost::accumulators::min(l_acc);
            p_max           = boost::accumulators::max(l_acc);
        }

        template<typename T> inline std::string Profile::convert( const T& p_in )
        {
            std::ostringstream os;
            os << p_in;
            return os.str();
        }

    #endif

#endif

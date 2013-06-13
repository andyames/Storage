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
    
        #define PROFILING               Benchmark<double> l_benchmark__LINE__(__PRETTY_FUNCTION__);
        #define PROFILINGNAME(name)     Benchmark<double> l_benchmark__LINE__(name);

        // http://c2.com/cgi/wiki?TooFewTemplateParameterLists
        #define PROFILINGINIT           template<> Profile<double>* Profile<double>::m_instance = new Profile<double>();
        #define PROFILINGCOUT           std::cout << *Profile<double>::getInstance() << std::endl;


        extern "C" {
            #if defined(_WIN32)
                #include <Windows.h>
    
            #elif defined(__unix__) || defined(__unix) || defined(unix) || (defined(__APPLE__) && defined(__MACH__))
                #include <unistd.h>
                #include <sys/types.h>
                #include <sys/param.h>
    
                #if defined(BSD)
                    #include <sys/sysctl.h>
                #endif
    
            #else
                #error "Unable to define getMemorySize( ) for an unknown OS."
            #endif
        }


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
        #include <boost/static_assert.hpp>
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
        
        #include "benchmark.hpp"


        // predeclation for class and operator<< overload
        // http://www.parashift.com/c++-faq-lite/template-friends.html
        //template<typename T> class Profile;
        //template<typename T> friend std::ostream& operator<< ( std::ostream&, const Profile<T>& );


        template<typename T> class Profile
        {
            BOOST_STATIC_ASSERT( !boost::is_integral<T>::value );
            
            public :
            
                typedef boost::accumulators::accumulator_set<T, boost::accumulators::stats< 
                    boost::accumulators::tag::count,
                    boost::accumulators::tag::sum,
                    boost::accumulators::tag::median, 
                    boost::accumulators::tag::mean, 
                    boost::accumulators::tag::variance,
                    boost::accumulators::tag::min,
                    boost::accumulators::tag::max
                    //boost::accumulators::tag::extended_p_square
                > > Accumulator;
            
                typedef std::map< std::string, Accumulator > DataMap;
            
            
                static void releaseInstance( void );
            
            
                static Profile<T>* getInstance( void )
                {
                    if (!m_instance) 
                        throw std::runtime_error("profiling instance does not exists");    
                    return m_instance;
                };
            
            
                static std::size_t getMemorySize(void)
                {
                    #if defined(_WIN32) && (defined(__CYGWIN__) || defined(__CYGWIN32__))
                        /* Cygwin under Windows. ------------------------------------ */
                        /* New 64-bit MEMORYSTATUSEX isn't available.  Use old 32.bit */
                        MEMORYSTATUS status;
                        status.dwLength = sizeof(status);
                        GlobalMemoryStatus( &status );
                        return (std::size_t)status.dwTotalPhys;
                    
                    #elif defined(_WIN32)
                        /* Windows. ------------------------------------------------- */
                        /* Use new 64-bit MEMORYSTATUSEX, not old 32-bit MEMORYSTATUS */
                        MEMORYSTATUSEX status;
                        status.dwLength = sizeof(status);
                        GlobalMemoryStatusEx( &status );
                        return (std::size_t)status.ullTotalPhys;
                    
                    #elif defined(__unix__) || defined(__unix) || defined(unix) || (defined(__APPLE__) && defined(__MACH__))
                        /* UNIX variants. ------------------------------------------- */
                        /* Prefer sysctl() over sysconf() except sysctl() HW_REALMEM and HW_PHYSMEM */
                        
                        #if defined(CTL_HW) && (defined(HW_MEMSIZE) || defined(HW_PHYSMEM64))
                            int mib[2];
                            mib[0] = CTL_HW;
                            #if defined(HW_MEMSIZE)
                                mib[1] = HW_MEMSIZE;            /* OSX. --------------------- */
                            #elif defined(HW_PHYSMEM64)
                                mib[1] = HW_PHYSMEM64;          /* NetBSD, OpenBSD. --------- */
                            #endif
                        
                            int64_t size = 0;               /* 64-bit */
                            std::size_t len = sizeof( size );
                            if ( sysctl( mib, 2, &size, &len, NULL, 0 ) == 0 )
                                return (std::size_t)size;
                        
                            throw std::runtime_error("can not determine memory size");
                    
                        #elif defined(_SC_AIX_REALMEM)
                            /* AIX. ----------------------------------------------------- */
                            return (std::size_t)sysconf( _SC_AIX_REALMEM ) * (size_t)1024L;
                        
                        #elif defined(_SC_PHYS_PAGES) && defined(_SC_PAGESIZE)
                            /* FreeBSD, Linux, OpenBSD, and Solaris. -------------------- */
                            return (std::size_t)sysconf( _SC_PHYS_PAGES ) * (std::size_t)sysconf( _SC_PAGESIZE );
                        
                        #elif defined(_SC_PHYS_PAGES) && defined(_SC_PAGE_SIZE)
                            /* Legacy. -------------------------------------------------- */
                            return (std::size_t)sysconf( _SC_PHYS_PAGES ) * (std::size_t)sysconf( _SC_PAGE_SIZE );
                        
                        #elif defined(CTL_HW) && (defined(HW_PHYSMEM) || defined(HW_REALMEM))
                            /* DragonFly BSD, FreeBSD, NetBSD, OpenBSD, and OSX. -------- */
                            int mib[2];
                            mib[0] = CTL_HW;
                            #if defined(HW_REALMEM)
                                mib[1] = HW_REALMEM;		/* FreeBSD. ----------------- */
                            #elif defined(HW_PYSMEM)
                                mib[1] = HW_PHYSMEM;		/* Others. ------------------ */
                            #endif
                        
                            unsigned int size = 0;		/* 32-bit */
                            std::size_t len = sizeof( size );
                            if ( sysctl( mib, 2, &size, &len, NULL, 0 ) == 0 )
                                return (size_t)size;
                        
                            throw std::runtime_error("can not determine memory size");
                        #endif /* sysctl and sysconf variants */
                    #endif
                    
                    return 0;
                };
            
            
                DataMap getTimes( void ) const { return m_times; }
            
            
                void setBenchmarkTime( const std::string& p_name, const T& p_time )
                {
                    m_locktimes.lock();
                    if (m_times.find(p_name) == m_times.end()) {
                        //boost::array<T, 3> probs = {0.25, 0.5, 0.75};
                        //m_times[p_name] = Accumulator( boost::accumulators::extended_p_square_probabilities = probs );
                        m_times[p_name] = Accumulator();
                    }
                    m_times[p_name](p_time);
                    m_locktimes.unlock();
                };
            
            
                // add data for http://de.wikipedia.org/wiki/Boxplot
                friend std::ostream& operator<< ( std::ostream& p_stream, const Profile& p )
                {
                    const std::size_t l_length      = 200;
                    const std::size_t l_first       = 25;
                    const std::size_t l_break       = 10;
                    const std::string l_columns[]   = { std::string("function name"),   std::string("call count"), 
                        std::string("accumulation"),    std::string("minimum"),
                        std::string("maximum"),         std::string("range"),
                        std::string("median"),          std::string("average"),
                        std::string("standard deviation")
                    };
                    const std::size_t l_columncount = sizeof(l_columns) / sizeof(std::string);
                    
                    
                    p_stream << std::left;
                    
                    // time performance
                    std::string l_help(" time performance (in ms) ");
                    p_stream << "\n===" << l_help << std::string(l_length-3-l_help.size(), '=')  << "\n";
                    for(std::size_t i=0; i < l_columncount; ++i)
                    {
                        p_stream << l_columns[i];
                        if (i < l_columncount - 1)
                            if (!i)
                                p_stream << std::string(l_break+l_first, ' ');
                            else 
                                p_stream << std::string(l_break, ' ');
                    }
                    p_stream << "\n\n";
                    
                    for(typename Profile<T>::DataMap::const_iterator it = p.m_times.begin(); it != p.m_times.end(); it++)
                    {
                        l_help = it->first.substr(0, l_first+l_break+l_columns[0].size()-1);
                        p_stream << l_help << std::string(l_first+l_break+l_columns[0].size()-l_help.size(), ' ');
                        
                        l_help = convert(boost::accumulators::count(it->second), 0);
                        p_stream << l_help << std::string(l_break+l_columns[1].size()-l_help.size(), ' ');
                        
                        l_help = convert(boost::accumulators::sum(it->second));
                        p_stream << l_help << std::string(l_break+l_columns[2].size()-l_help.size(), ' ');
                        
                        l_help = convert(boost::accumulators::min(it->second));
                        p_stream << l_help << std::string(l_break+l_columns[3].size()-l_help.size(), ' ');
                        
                        l_help = convert(boost::accumulators::max(it->second));
                        p_stream << l_help << std::string(l_break+l_columns[4].size()-l_help.size(), ' ');
                        
                        l_help = convert(boost::accumulators::max(it->second)-boost::accumulators::min(it->second));
                        p_stream << l_help << std::string(l_break+l_columns[5].size()-l_help.size(), ' ');
                        
                        l_help = convert(boost::accumulators::median(it->second));
                        p_stream << l_help << std::string(l_break+l_columns[6].size()-l_help.size(), ' ');
                        
                        l_help = convert(boost::accumulators::mean(it->second) );
                        p_stream << l_help << std::string(l_break+l_columns[7].size()-l_help.size(), ' ');
                        
                        l_help = convert(sqrt(boost::accumulators::variance(it->second)));
                        p_stream << l_help << std::string(l_break+l_columns[8].size()-l_help.size(), ' ');
                        
                        p_stream << "\n";
                    }
                    
                    
                    // memory performance
                    l_help = " memory usage ";
                    p_stream << "\n\n\n===" << l_help << std::string(l_length-3-l_help.size(), '=') << std::endl;
                    p_stream << "physical memory (bytes) :" << std::string(3, ' ') << getMemorySize() << std::endl;
                    
                    return p_stream;
                };

            
            
            
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
            
                
            
                static Profile<T>* m_instance;

                Spinlock m_locktimes;
                DataMap m_times;
                DataMap m_memory;

            
                Profile( void ) : m_locktimes(), m_times(), m_memory() {};
                ~Profile( void ) {};
                Profile( const Profile& ) {};
                Profile& operator=( const Profile& );
                
                static std::string convert( const T& p_in, const std::size_t& p = 5 )
                {
                    std::ostringstream os;
                    os << std::fixed << std::setprecision(p) << p_in;
                    return os.str();
                };
        };


    #endif

#endif

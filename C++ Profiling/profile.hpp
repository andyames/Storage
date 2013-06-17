#ifndef BENCHMARK

    #define PROFILING
    #define PROFILINGNAME(name)
    #define PROFILINGINITIALISATION
    #define PROFILINGCOUT

#else
    
    #ifndef __PROFILE
    #define __PROFILE
    
        #define PROFILING                   Benchmark<> l_benchmark__LINE__(__PRETTY_FUNCTION__);
        #define PROFILINGNAME(name)         Benchmark<> l_benchmark__LINE__(name);
        #define PROFILINGINITIALISATION     template<> boost::shared_ptr< Profile<> > Profile<>::m_instance = boost::shared_ptr< Profile<> >(new Profile<>());
        #define PROFILINGCOUT               std::cout << *Profile<>::getInstance() << std::endl;


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
        #include <boost/array.hpp>
        #include <boost/atomic.hpp>
        #include <boost/shared_ptr.hpp>
        #include <boost/static_assert.hpp>
        #include <boost/accumulators/statistics.hpp>
        #include <boost/accumulators/accumulators.hpp>

        #include "benchmark.hpp"

        namespace bac = boost::accumulators;


        /** profiling singleton class, that collects all time & memory information **/
        template<typename T = double, std::size_t LOWERQUANTIL=2500, std::size_t UPPERQUANTIL=7500> class Profile
        {
            BOOST_STATIC_ASSERT( !boost::is_integral<T>::value );
            BOOST_STATIC_ASSERT( LOWERQUANTIL < UPPERQUANTIL );
            BOOST_STATIC_ASSERT( UPPERQUANTIL <= 10000 );
            
            public :
            
                /** typedef of the statistic accumulator - median is set in the 0.5-quantil **/
                typedef bac::accumulator_set<T, bac::stats< 
                    bac::tag::count,
                    bac::tag::sum,
                    bac::tag::mean, 
                    bac::tag::median,
                    bac::tag::variance,
                    bac::tag::min,
                    bac::tag::max,
                    bac::tag::extended_p_square_quantile
                > > Accumulator;
            
                /** typdef of the map & accumulator **/
                typedef std::map< std::string, Accumulator > DataMap;
            
            
                /** returns the data
                 * @param datamap
                 **/
                DataMap getTimes( void ) const { return m_times; }
            
            
                /** returns the instance pointer
                 * @return pointer to the instance
                 **/
                static Profile<T>* getInstance( void ) { return m_instance.get(); };

                
                /** sets the time
                 * @param p_name name of the timeset
                 * @param p_time time value
                 **/
                void setBenchmarkTime( const std::string& p_name, const T& p_time )
                {
                    m_locktimes.lock();
                    
                    typename DataMap::iterator it = m_times.find(p_name);
                    if (it != m_times.end())
                        it->second(p_time);
                    else {
                        // set lower & upper quantil and 0.5-quantil for median
                        const boost::array<T,3> probs = {static_cast<T>(LOWERQUANTIL) / 10000, static_cast<T>(0.5), static_cast<T>(UPPERQUANTIL) / 10000};
                        
                        Accumulator l_acc( bac::extended_p_square_probabilities = probs );
                        l_acc(p_time);
                        m_times.insert( std::pair<std::string,Accumulator>(p_name, l_acc) );
                    }
                    
                    m_locktimes.unlock();
                };
            

                /** read the size of the main memory
                 * @param return memory size in bytes
                 **/
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
            
            
                /** stream operator for http://en.wikipedia.org/wiki/Box_plot
                 * @param p_stream input stream
                 * @param p object
                 * @return updated stream
                 **/
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
                        
                        l_help = convert(bac::count(it->second), 0);
                        p_stream << l_help << std::string(l_break+l_columns[1].size()-l_help.size(), ' ');
                        
                        l_help = convert(bac::sum(it->second));
                        p_stream << l_help << std::string(l_break+l_columns[2].size()-l_help.size(), ' ');
                        
                        l_help = convert(bac::min(it->second));
                        p_stream << l_help << std::string(l_break+l_columns[3].size()-l_help.size(), ' ');
                        
                        l_help = convert(bac::max(it->second));
                        p_stream << l_help << std::string(l_break+l_columns[4].size()-l_help.size(), ' ');
                        
                        l_help = convert(bac::max(it->second)-boost::accumulators::min(it->second));
                        p_stream << l_help << std::string(l_break+l_columns[5].size()-l_help.size(), ' ');
                        
                        //l_help = convert(bac::median(it->second));
                        l_help = convert(bac::quantile(it->second, bac::quantile_probability = static_cast<T>(0.5)));
                        p_stream << l_help << std::string(l_break+l_columns[6].size()-l_help.size(), ' ');
                        
                        l_help = convert(bac::mean(it->second) );
                        p_stream << l_help << std::string(l_break+l_columns[7].size()-l_help.size(), ' ');
                        
                        l_help = convert(sqrt(bac::variance(it->second)));
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
            
                /** class for spinlocks **/
                class Spinlock {
                    
                    public :
                    
                    /** ctor of the spinlock **/
                    Spinlock( void ) : m_state(Unlocked) {};
                    /** dtor of the spinlock with explicit realsing lock **/
                    ~Spinlock( void ) { unlock(); };
                    
                    /** lock the object **/
                    void lock( void )
                    {
                        while (m_state.exchange(Locked, boost::memory_order_relaxed) == Locked)
                            __asm__ __volatile__ ("rep; nop" : : );
                        atomic_thread_fence(boost::memory_order_acquire);     
                    };
                    
                    /** unlock the object **/
                    void unlock( void ) { m_state.store(Unlocked, boost::memory_order_release); };
                    
                    
                    private :
                    
                        /** typedef of lock definition **/
                        typedef enum {Locked, Unlocked} LockState;
                        /** locking state **/
                        boost::atomic<LockState> m_state;
                    
                };
                
                
                /** static definition of the profile object pointer **/
                static boost::shared_ptr< Profile<T> > m_instance;
                
                /** spinlock of the time object **/
                Spinlock m_locktimes;
                
                /** map of the times **/
                DataMap m_times;
                
                /** map of the memory values **/
                DataMap m_memory;
                
                
                /** ctor **/
                Profile( void ) : m_locktimes(), m_times(), m_memory() {};
                /** copy-ctor **/
                Profile( const Profile& ) {};
                /** equal operator **/
                Profile& operator=( const Profile& );
                
                /** convert method for numerical values
                 * @param value
                 * @param p precision
                 * @return string with converted value
                 **/
                static std::string convert( const T& p_in, const std::size_t& p = 5 )
                {
                    std::ostringstream os;
                    os << std::fixed << std::setprecision(p) << p_in;
                    return os.str();
                };
            

        };


    #endif

#endif

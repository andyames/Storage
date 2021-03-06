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
                
                #if defined(BSD) || (defined(__APPLE__) && defined(__MACH__))
                    #include <sys/sysctl.h>
                #endif

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

    
        /** type of the memory byte scale **/
        enum MemorySizeScale {
            byte = 1,
            KiB  = 1024,
            MiB  = 1048576,
            GiB  = 1073741824
        };


        /** profiling singleton class, that collects all time & memory information **/
        template<typename T = double, MemorySizeScale MEMSCALE=MiB> class Profile
        {
            BOOST_STATIC_ASSERT( !boost::is_integral<T>::value );

            
            public :

                /** typedef of the statistic accumulator - median is set in the 0.5-quantil **/
                typedef bac::accumulator_set<T, bac::stats<
                    bac::tag::count,
                    bac::tag::sum,
                    bac::tag::mean,
                    bac::tag::median,
                    bac::tag::variance,
                    bac::tag::min,
                    bac::tag::max
                > > Accumulator;

            
                /** typdef of the map & accumulator **/
                typedef std::map< std::string, Accumulator > DataMap;


                /** returns the time data
                 * @param datamap
                 **/
                DataMap getTimes( void ) const { return m_times; }
            
                
                /** return the resident set size memory data
                 * @param datamap
                 **/
                DataMap getResidentSetMemory( void ) const { return m_rssmemory; }
            
            
                /** returns the instance pointer
                 * @return pointer to the instance
                 **/
                static Profile<T, MEMSCALE>* getInstance( void ) { return m_instance.get(); };

                
                /** sets the time (is set in milliseconds)
                 * @param p_name name of the time set
                 * @param p_time time value
                 **/
                void setBenchmarkTime( const std::string& p_name, const T& p_time )
                {
                    m_locktimes.lock();
                    
                    typename DataMap::iterator it = m_times.find(p_name);
                    if (it != m_times.end())
                        it->second(p_time);
                    else {
                        Accumulator l_acc;
                        l_acc(p_time);
                        m_times.insert( std::pair<std::string,Accumulator>(p_name, l_acc) );
                    }
                    
                    m_locktimes.unlock();
                };
            
                
                /** sets the resident set size of the memory (in KiB)
                 * @param p_name of the memory set
                 * @param p_mem memory value
                 **/
                void setBenchmarkResidentSetSize( const std::string& p_name, const T& p_mem )
                {
                    m_lockrssmemory.lock();
                    
                    typename DataMap::iterator it = m_rssmemory.find(p_name);
                    if (it != m_rssmemory.end())
                        it->second( static_cast<T>(p_mem) / MEMSCALE );
                    else {
                        Accumulator l_acc;
                        l_acc( static_cast<T>(p_mem) / MEMSCALE );
                        m_rssmemory.insert( std::pair<std::string,Accumulator>(p_name, l_acc) );
                    }
                    
                    m_lockrssmemory.unlock();
                }
            

                /** returns a map with system information
                 * @warn system information must be implementated OS specific
                 * Mac OS X system information @see https://developer.apple.com/library/mac/#documentation/Darwin/Reference/ManPages/man3/sysctlbyname.3.html
                 * @return information map
                 **/
                static std::map<std::string, std::string> getSystemInformation(void)
                {
                    std::map<std::string, std::string> l_info;

                    #if (defined(__APPLE__) && defined(__MACH__))
                    
                        std::size_t l_cpus    = 0;
                        std::size_t l_lencpus = sizeof(l_cpus);
                        if (!sysctlbyname("hw.physicalcpu_max", &l_cpus, &l_lencpus, NULL, 0))
                            l_info["physical cpu(s)"] = convert(l_cpus, 0);
                        
                        std::size_t l_mem    = 0;
                        std::size_t l_lenmem = sizeof(l_mem);
                        if (!sysctlbyname("hw.memsize", &l_mem, &l_lenmem, NULL, 0))
                            l_info["physical memory ("+byteName()+")"] = convert( static_cast<T>(l_mem) / MEMSCALE, 2);
                    
                        std::size_t l_umem    = 0;
                        std::size_t l_lenumem = sizeof(l_mem);
                        if (!sysctlbyname("hw.usermem", &l_umem, &l_lenumem, NULL, 0))
                            l_info["non-kernel memory ("+byteName()+")"] = convert( static_cast<T>(l_umem) / MEMSCALE, 2);
                        
                        std::size_t l_page    = 0;
                        std::size_t l_lenpage = sizeof(l_page);
                        if (!sysctlbyname("hw.pagesize", &l_page, &l_lenpage, NULL, 0))
                            l_info["page size (bytes)"] = convert( static_cast<T>(l_page), 0);
                    
                        std::size_t l_conproc    = 0;
                        std::size_t l_lenconproc = sizeof(l_conproc);
                        if (!sysctlbyname("kern.maxproc", &l_conproc, &l_lenconproc, NULL, 0))
                            l_info["number concurrent processes"] = convert( l_conproc, 0);
                    
                        size_t l_lenosname = 0;
                        sysctlbyname("kern.ostype", NULL, &l_lenosname, NULL, 0);
                        if (l_lenosname) {
                            char* l_osname = static_cast<char*>(malloc( l_lenosname * sizeof(char) ));
                            sysctlbyname("kern.ostype", l_osname, &l_lenosname, NULL, 0);
                            l_info["OS name"] = std::string(l_osname);
                            delete(l_osname);
                        }
                    
                        size_t l_lenosrelease = 0;
                        sysctlbyname("kern.osrelease", NULL, &l_lenosrelease, NULL, 0);
                        if (l_lenosrelease) {
                            char* l_osrelease = static_cast<char*>(malloc( l_lenosrelease * sizeof(char) ));
                            sysctlbyname("kern.osrelease", l_osrelease, &l_lenosrelease, NULL, 0);
                            l_info["OS release"] = std::string(l_osrelease);
                            delete(l_osrelease);
                        }
                    
                        size_t l_lenkernel = 0;
                        sysctlbyname("kern.version", NULL, &l_lenkernel, NULL, 0);
                        if (l_lenkernel) {
                            char* l_kernel = static_cast<char*>(malloc( l_lenkernel * sizeof(char) ));
                            sysctlbyname("kern.version", l_kernel, &l_lenkernel, NULL, 0);
                            l_info["Kernel"] = std::string(l_kernel);
                            delete(l_kernel);
                        }
                    

                    #else
                        #error "Unable to define getSystemInformation() for an unkown OS."
                    #endif
                    
                    
                    return l_info;
                };
            
            
                /** stream operator for output
                 * @param p_stream output stream
                 * @param p object
                 * @return updated stream
                 **/
                friend std::ostream& operator<< ( std::ostream& p_stream, const Profile& p )
                {
                    p.createTableLayout( p_stream, std::string("time performance (in ms)"), p.m_times);
                    p_stream << "\n\n";
                    p.createTableLayout( p_stream, std::string("resident set size usage (in " + Profile<T, MEMSCALE>::byteName() + ")"), p.m_rssmemory);
                    p_stream << "\n\n";
                    p.createListLayout( p_stream, std::string("system information"), p.getSystemInformation() );
                    
                    return p_stream;
                };
            
            
            private :
            
                /** class for spinlocks
                 * @see http://www.codeproject.com/Articles/184046/Spin-Lock-in-C
                 **/
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
                static boost::shared_ptr< Profile<T, MEMSCALE> > m_instance;
                
                /** spinlock of the time object **/
                Spinlock m_locktimes;
            
                /** spinlock of the rss memory object **/
                Spinlock m_lockrssmemory;
                
                /** map of the times **/
                DataMap m_times;
                
                /** map of the memory values **/
                DataMap m_rssmemory;
                
                
                /** ctor **/
                Profile( void ) : m_locktimes(), m_lockrssmemory(), m_times(), m_rssmemory() {};
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
            
            
                /** returns string name of the memscale enum
                 * @param p_in memory scale
                 * @return string name
                 **/
                static std::string byteName( void )
                {
                    switch (MEMSCALE) {
                        case byte : return std::string("bytes"); break;
                        case KiB  : return std::string("KiB");   break;
                        case MiB  : return std::string("MiB");   break;
                        case GiB  : return std::string("GiB");   break;
                    }
                    
                    return std::string();
                };


                /** private method for list output
                 * @param p_stream stream object
                 * @param p_head table head
                 * @param p_data data
                 * @param p_length max line length
                 * @param p_first length of the first column
                 * @param p_break seperator size between columns
                 * @param p_firstcolumnsize size / length of the first column
                 **/
                void createListLayout( std::ostream& p_stream, const std::string& p_head, const std::map<std::string, std::string>& p_data, const std::size_t& p_length = 200, const std::size_t& p_first = 25, const std::size_t& p_break = 10, const std::size_t& p_firstcolumnsize = 13 ) const
                {
                    p_stream << std::left << "\n=== " << p_head << " " << std::string(p_length-3-p_head.size(), '=')  << "\n";

                    for(std::map<std::string, std::string>::const_iterator it = p_data.begin(); it != p_data.end(); it++)
                        p_stream << it->first << std::string(p_first+p_break+p_firstcolumnsize-it->first.size(), ' ') << it->second << "\n";
                }


                /** private method for table output
                 * @param p_stream stream object
                 * @param p_head table head
                 * @param p_data data
                 * @param p_length max line length
                 * @param p_first length of the first column
                 * @param p_break seperator size between columns
                 **/
                void createTableLayout( std::ostream& p_stream, const std::string& p_head, const DataMap& p_data, const std::size_t& p_length = 200, const std::size_t& p_first = 25, const std::size_t& p_break = 10 ) const
                {

                    const std::string l_columns[]   = {
                        std::string("function name"),   std::string("call count"),
                        std::string("accumulation"),    std::string("minimum"),
                        std::string("maximum"),         std::string("range"),
                        std::string("median"),          std::string("average"),
                        std::string("standard deviation")
                    };
                    const std::size_t l_columncount = sizeof(l_columns) / sizeof(std::string);

                    
                    // create head
                    p_stream << std::left << "\n=== " << p_head << " " << std::string(p_length-3-p_head.size(), '=')  << "\n";
                    for(std::size_t i=0; i < l_columncount; ++i)
                    {
                        p_stream << l_columns[i];
                        if (i < l_columncount - 1)
                            if (!i)
                                p_stream << std::string(p_break+p_first, ' ');
                            else
                                p_stream << std::string(p_break, ' ');
                    }
                    p_stream << "\n\n";


                    // data
                    for(typename Profile<T, MEMSCALE>::DataMap::const_iterator it = p_data.begin(); it != p_data.end(); it++)
                    {
                        std::string l_help;

                        l_help = it->first.substr(0, p_first+p_break+l_columns[0].size()-1);
                        p_stream << l_help << std::string(p_first+p_break+l_columns[0].size()-l_help.size(), ' ');

                        l_help = convert(bac::count(it->second), 0);
                        p_stream << l_help << std::string(p_break+l_columns[1].size()-l_help.size(), ' ');

                        l_help = convert(bac::sum(it->second));
                        p_stream << l_help << std::string(p_break+l_columns[2].size()-l_help.size(), ' ');

                        l_help = convert(bac::min(it->second));
                        p_stream << l_help << std::string(p_break+l_columns[3].size()-l_help.size(), ' ');

                        l_help = convert(bac::max(it->second));
                        p_stream << l_help << std::string(p_break+l_columns[4].size()-l_help.size(), ' ');

                        l_help = convert(bac::max(it->second)-boost::accumulators::min(it->second));
                        p_stream << l_help << std::string(p_break+l_columns[5].size()-l_help.size(), ' ');

                        l_help = convert(bac::median(it->second));
                        p_stream << l_help << std::string(p_break+l_columns[6].size()-l_help.size(), ' ');

                        l_help = convert(bac::mean(it->second));
                        p_stream << l_help << std::string(p_break+l_columns[7].size()-l_help.size(), ' ');

                        l_help = convert(sqrt(bac::variance(it->second)));
                        p_stream << l_help << std::string(p_break+l_columns[8].size()-l_help.size(), ' ');

                        p_stream << "\n";
                        
                    }
                }

            
        };


    #endif

#endif

#ifdef BENCHMARK

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

    #include <stdexcept>
    #include "profile.h"



    Profile* Profile::getInstance( void )
    { 
        if (!m_instance) 
            throw std::runtime_error("profiling instance does not exists");    
        return m_instance;
    }


    std::map<std::string, std::vector<unsigned long long> > Profile::getTimes( void ) const { return m_times; }


    std::map<std::string, std::vector<unsigned long long> > Profile::getMemory( void ) const { return m_memory; }

    std::map<std::string, unsigned long long> Profile::getCalls( void ) const { return m_calls; }


    void Profile::setBenchmarkTime( const std::string& p_name, const unsigned long long& p_time )
    {
        m_lockcalls.lock();
        if (m_calls.find(p_name) == m_calls.end())
            m_calls[p_name] = 0;
        m_calls[p_name]++;
        m_lockcalls.unlock();
        
        m_locktimes.lock();
        if (m_times.find(p_name) == m_times.end())
            m_times[p_name] = std::vector<unsigned long long>(); 
        m_times[p_name].push_back(p_time);
        m_locktimes.unlock();
    }


    std::size_t Profile::getMemorySize(void)
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
        
        return 0L;
    }


    std::string Profile::repeat( const std::size_t& p_times, const std::string& p_str )
    {
        std::ostringstream os;
        for(int i = 0; i < p_times; i++)
            os << p_str;
        return os.str();
    }


    std::ostream& operator<< ( std::ostream& p_stream, const Profile& p )
    {
        const std::size_t l_break       = 20;
        const std::string l_columns[]   = { std::string("function name [call count / acc. cycles]"), std::string("minimum"), std::string("maximum"), std::string("median"), std::string("average"), std::string("standard deviation") };
        const std::size_t l_columncount = sizeof(l_columns) / sizeof(std::string);
        
        // time performance
        std::string l_help(" time performance (cpu cycles) ");
        p_stream << "\n---" << l_help << Profile::repeat(220-3-l_help.size(), "-") << "\n";
        for(std::size_t i=0; i < l_columncount; ++i)
        {
            p_stream << l_columns[i];
            if (i < l_columncount - 1)
                p_stream << Profile::repeat(l_break);
        }
        p_stream << "\n\n";
            
        for(std::map< std::string, std::vector<unsigned long long> >::const_iterator it = p.m_times.begin(); it != p.m_times.end(); it++)
        {
            if (it->second.empty())
                continue;
            
            double l_avg, l_stddev;
            unsigned long long l_median, l_min, l_max, l_sum;
            Profile::AverageDerivationMedian(it->second, l_avg, l_stddev, l_median, l_min, l_max, l_sum);
            
            
            l_help = it->first + " [" + Profile::convert( p.m_calls.find(it->first)->second ) + " / " + Profile::convert(l_sum) + "]";
            p_stream << l_help << Profile::repeat(l_break+l_columns[0].size()-l_help.size());
            
            l_help = Profile::convert(l_min);
            p_stream << l_help << Profile::repeat(l_break+l_columns[1].size()-l_help.size());
            
            l_help = Profile::convert(l_max);
            p_stream << l_help << Profile::repeat(l_break+l_columns[1].size()-l_help.size());
            
            l_help = Profile::convert(l_median);
            p_stream << l_help << Profile::repeat(l_break+l_columns[1].size()-l_help.size());
            
            l_help = Profile::convert(l_avg);
            p_stream << l_help << Profile::repeat(l_break+l_columns[2].size()-l_help.size());
            
            l_help = Profile::convert(l_stddev);
            p_stream << l_help << Profile::repeat(l_break+l_columns[3].size()-l_help.size());
            
            p_stream << "\n";
        }
        
        
        // memory performance
        l_help = " memory usage ";
        p_stream << "\n\n\n---" << l_help << Profile::repeat(220-3-l_help.size(), "-") << "\n";
        p_stream << "physical memory (bytes) : " << Profile::repeat(2) << Profile::getMemorySize() << "\n";
        
        return p_stream;
    }

#endif
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


    void Profile::setBenchmarkTime( const std::string& p_name, const double& p_time )
    {
        m_locktimes.lock();
        if (m_times.find(p_name) == m_times.end())
            m_times[p_name] = Accumulator();
        m_times[p_name](p_time);
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
        
        return 0;
    }


    std::ostream& operator<< ( std::ostream& p_stream, const Profile& p )
    {
        const std::size_t l_length      = 215;
        const std::size_t l_first       = 25;
        const std::size_t l_break       = 15;
        const std::string l_columns[]   = { std::string("function name"), std::string("call count"), std::string("accumulation"), std::string("minimum"), std::string("maximum"), std::string("median"), std::string("average"), std::string("standard deviation") };
        const std::size_t l_columncount = sizeof(l_columns) / sizeof(std::string);


        p_stream << std::left;
        
        // time performance
        std::string l_help(" time performance (in ms) ");
        p_stream << "\n---" << l_help << std::string(l_length-3-l_help.size(), '-')  << "\n";
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
            
        for(std::map< std::string, Profile::Accumulator >::const_iterator it = p.m_times.begin(); it != p.m_times.end(); it++)
        {
            l_help = it->first.substr(0, l_first+l_break+l_columns[0].size()-1);
            p_stream << l_help << std::string(l_first+l_break+l_columns[0].size()-l_help.size(), ' ');
            
            l_help = Profile::convert(boost::accumulators::count(it->second));
            p_stream << l_help << std::string(l_break+l_columns[1].size()-l_help.size(), ' ');

            l_help = Profile::convert(boost::accumulators::sum(it->second));
            p_stream << l_help << std::string(l_break+l_columns[2].size()-l_help.size(), ' ');
            
            l_help = Profile::convert(boost::accumulators::min(it->second));
            p_stream << l_help << std::string(l_break+l_columns[3].size()-l_help.size(), ' ');
            
            l_help = Profile::convert(boost::accumulators::max(it->second));
            p_stream << l_help << std::string(l_break+l_columns[4].size()-l_help.size(), ' ');
            
            l_help = Profile::convert(boost::accumulators::median(it->second));
            p_stream << l_help << std::string(l_break+l_columns[5].size()-l_help.size(), ' ');
            
            l_help = Profile::convert(boost::accumulators::mean(it->second) );
            p_stream << l_help << std::string(l_break+l_columns[6].size()-l_help.size(), ' ');
            
            l_help = Profile::convert(sqrt(boost::accumulators::variance(it->second)));
            p_stream << l_help << std::string(l_break+l_columns[7].size()-l_help.size(), ' ');
            
            p_stream << "\n";
        }
        
        
        // memory performance
        l_help = " memory usage ";
        p_stream << "\n\n\n---" << l_help << std::string(l_length-3-l_help.size(), '-') << std::endl;
        p_stream << "physical memory (bytes) :" << std::string(3, ' ') << Profile::getMemorySize() << std::endl;
        
        return p_stream;
    }

#endif
#ifdef BENCHMARK

    #include "benchmark.h"

    Benchmark::Benchmark( const std::string& p_functionname ) : 
        m_functionname(p_functionname), 
        m_starttime(getCycles())
    {};


    Benchmark::~Benchmark( void )
    {
        unsigned long long l_endtime = getCycles();
        Profile::getInstance()->setBenchmarkTime( m_functionname, getCPUFrequencyScale() * (l_endtime-m_starttime) );
    };


    double Benchmark::getCPUFrequencyScale( void )
    {
        // http://msdn.microsoft.com/en-us/library/windows/desktop/ms644905(v=vs.85).aspx
        // http://developer.apple.com/library/mac/#qa/qa1398/_index.html  / http://www.macresearch.org/tutorial_performance_and_time 
        
        double l_scale = 1;
        
        #if defined(__APPLE__) && defined(__MACH__)
            mach_timebase_info_data_t l_timeinfo;
            if (!mach_timebase_info( &l_timeinfo ))
                l_scale =  1e-6 * static_cast<double>(l_timeinfo.numer) / l_timeinfo.denom; 
        #endif

        return l_scale;
    }

#endif


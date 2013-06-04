#ifdef BENCHMARK

    #include "profile.h"

    Profile* Profile::getInstance( void )
    { 
        if (!m_instance) 
            throw std::runtime_error("profiling instance does not exists");    
        return m_instance;
    }


    void Profile::createInstance( void )
    {
        if (!m_instance)
            m_instance = new Profile();
    }


    void Profile::releaseInstance( void )
    {
        delete m_instance;
    }


    std::map<std::string, std::vector<unsigned long long> > Profile::getTimes( void ) const { return m_times; }


    std::map<std::string, std::vector<unsigned long long> > Profile::getMemory( void ) const { return m_memory; }


    void Profile::setBenchmarkTime( const std::string& p_name, const unsigned long long& p_time )
    {
        m_locktimes.lock();
        if (m_times.find(p_name) == m_times.end())
            m_times[p_name] = std::vector<unsigned long long>(); 
        m_times[p_name].push_back(p_time);
        m_locktimes.unlock();
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
        const std::size_t l_break       = 15;
        const std::string l_columns[]   = { std::string("function name"), std::string("minimum"), std::string("maximum"), std::string("median"), std::string("average"), std::string("standard deviation") };
        const std::size_t l_columncount = sizeof(l_columns) / sizeof(std::string);
        
        std::string l_help(" time performance ");
        p_stream << "\n---" << l_help << Profile::repeat(160-3-l_help.size(), "-") << "\n";
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
            unsigned long long l_median, l_min, l_max;
            Profile::AverageDerivationMedian(it->second, l_avg, l_stddev, l_median, l_min, l_max);
            
            
            p_stream << it->first << Profile::repeat(l_break+l_columns[0].size()-it->first.size());
            
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
        
        
        return p_stream;
    }

#endif
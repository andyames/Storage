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


void Profile::AverageDerivationMedian( const std::vector<unsigned long long>& p_vec, double& p_average, double& p_stdderivation, unsigned long long& p_median )
{
    double sum = std::accumulate(p_vec.begin(), p_vec.begin(), 0.0);
    p_average  =  sum / p_vec.size();
    double accum = 0.0;
    
    //Lambda call - only with  C++0x: std::for_each(p_vec.begin(), p_vec.end(), [&accum](const double& d) { accum += (d - p_average) * (d - p_average); });
    BOOST_FOREACH( double d, p_vec )
        accum += (d - p_average) * (d - p_average);
    
    p_stdderivation = sqrt(accum / (p_vec.size()-1));
    p_median        = p_vec[(p_vec.size()-1)/2];
}


std::map<std::string, std::vector<unsigned long long> > Profile::getTimes( void ) const { return m_times; }


std::map<std::string, std::vector<unsigned long long> > Profile::getMemory( void ) const { return m_memory; }


void Profile::setBenchmarkTime( const std::string& p_name, const unsigned long long& p_time )
{
    boost::lock_guard<boost::mutex> l_lock(m_muxtimes);
    if (m_times.find(p_name) == m_times.end())
        m_times[p_name] = std::vector<unsigned long long>(); 
    m_times[p_name].push_back(p_time);
}



std::ostream& operator<< ( std::ostream& p_stream, const Profile& p )
{
    p_stream << "time performance\n\n";
    p_stream << "------------------------------------------------------------------------------------------------------------------------\n";
    p_stream << "function name\t\t\tmedian\t\t\taverage\t\t\tstandard deviation\n\n";
    
    for(std::map< std::string, std::vector<unsigned long long> >::const_iterator it = p.m_times.begin(); it != p.m_times.end(); it++)
    {
        if (it->second.empty())
            continue;
        
        double l_avg;
        double l_stddev;
        unsigned long long l_median;
        Profile::AverageDerivationMedian(it->second, l_avg, l_stddev, l_median);
        p_stream << it->first << "\t\t\t" << l_median << "\t\t\t" << l_avg << "\t\t\t" << l_stddev << "\n";
    }
    
    
    p_stream << "\n\n\nmemory usage\n\n";
    p_stream << "------------------------------------------------------------------------------------------------------------------------\n";
    p_stream << "function name\t\t\tmedian\t\t\taverage\t\t\tstandard deviation\n\n";
    
    for(std::map< std::string, std::vector<unsigned long long> >::const_iterator it = p.m_memory.begin(); it != p.m_memory.end(); it++)
    {
        if (it->second.empty())
            continue;
        
        double l_avg;
        double l_stddev;
        unsigned long long l_median;
        Profile::AverageDerivationMedian(it->second, l_avg, l_stddev, l_median);
        p_stream << it->first << "\t\t\t" << l_median << "\t\t\t" << l_avg << "\t\t\t" << l_stddev << "\n";
    }
    
    return p_stream;
}
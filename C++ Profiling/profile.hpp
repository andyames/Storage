#ifndef BENCHMARK

    #define PROFILE

#else
    
    #ifndef __BENCHMARKPROFILE
    #define __BENCHMARKPROFILE
    
        #define PROFILE() Benchmark l_benchmark__LINE__( __FUNCTION __ );


        #include <map>
        #include <vector>
        #include <string>
        #include <numeric>
        #include <iostream>
        #include <stdexcept>
        #include <boost/thread.hpp>
        //#include <boost/shared_ptr.hpp>

        class Profile;


        class Benchmark
        {
            public :
            
                Benchmark( const std::string& p_functionname ) : m_functionname(p_functionname), m_starttime(getCycles()) {};
                ~Benchmark( void ) { m_endtime = getCycles(); Profile::getInstance()->setBechmarkTime( m_functionname, m_endtime-m_starttime); };

            
            private :
            
                const std::string m_functionname;
        
                unsigned long long m_starttime;
            
                unsigned long long m_endtime;
        
        };



        class Profile
        {
            public :
            
                static void createInstance( void ) { if (!m_instance) m_instance = new Profile(); }
                static void releaseInstance( void ) { delete m_instance; };
            
                static Profile* getInstance( void ) { 
                    if (!m_instance) 
                        throw std::runtime_error("profiling instance does not exists");    
                    return m_instance;
                };
            
                std::map<std::string, std::vector<unsigned long long> > getTimes( void ) const { return m_times; };
                std::map<std::string, std::vector<unsigned long long> > getMemory( void ) const { return m_memory; };
            
                void setBenchmarkTime( const std::string& p_name, const unsigned long long& p_time )
                {
                    boost::lock_guard<boost::mutex> l_lock(m_muxtimes);
                    if (m_times.find(p_name) == m_times.end())
                        m_times[p_name] = std::vector<unsigned long long>(); 
                    m_times[p_name].push_back(p_time);
                }; 
            
                //void setBenchmarkMemory( const std::string& p_name, ??? )
                //boost::shared_ptr<Benchmark> benchmark( const std::string& ) const;
                
            
                friend std::ostream& operator<< ( std::ostream& p_stream, const Profile& p )
                {
                    p_stream << "time performance\n\n";
                    p_stream << "------------------------------------------------------------------------------------------------------------------------\n";
                    p_stream << "function name\t\t\tmedian\t\t\taverage\t\t\tstandard deviation\n\n";
                    
                    for(std::map< std::string, std::vector<unsigned long long> >::const_iterator it = p.m_times.begin(); it != m_times.end(), it++)
                    {
                        if (it->second.empty())
                            continue;
                        
                        double l_avg;
                        double l_stddev;
                        unsigned long long l_median;
                        AverageDerivationMedian<unsigned long long>(it->second, l_avg, l_stddev, l_median);
                        p_stream << it->first << "\t\t\t" << l_median << "\t\t\t" << l_avg << "\t\t\t" << l_stddev << "\n";
                    }
                    
                    
                    p_stream << "\n\n\nmemory usage\n\n";
                    p_stream << "------------------------------------------------------------------------------------------------------------------------\n";
                    p_stream << "function name\t\t\tmedian\t\t\taverage\t\t\tstandard deviation\n\n";
                    
                    for(std::map< std::string, std::vector<unsigned long long> >::const_iterator it = p.m_memory.begin(); it != m_memory.end(), it++)
                    {
                        if (it->second.empty())
                            continue;
                        
                        double l_avg;
                        double l_stddev;
                        unsigned long long l_median;
                        AverageDerivationMedian<unsigned long long>(it->second, l_avg, l_stddev, l_median);
                        p_stream << it->first << "\t\t\t" << l_median << "\t\t\t" << l_avg << "\t\t\t" << l_stddev << "\n";
                    }
                    
                    return p_stream;
                };

            
            
            
            private :
                
                Profile( void ) : m_muxtimes(), m_muxmemory(), m_times(), m_memory() {};
                ~Profile( void ); 
                Profile( const Profile& ) {};
                Profile& operator=( const Profile& );
            
                template<typename T> static void AverageDerivationMedian( const std::vector<T> p_vec, double& p_average, double& p_stdderivation, T& p_median )
                {
                    double sum = std::accumulate(p_vec.begin(), p_vec.begin(), 0.0);
                    p_average  =  sum / p_vec.size();
                    double accum = 0.0;
                    
                    std::for_each(p_vec.begin(), p_vec.end(), [&](const double d) { accum += (d - p_average) * (d - p_average); });
                    
                    p_stdderivation = sqrt(accum / (p_vec.size()-1));
                    p_median        = p_vec[(p_vec.size()-1)/2];
                }
            
            
            
                static Profile* m_instance;
                boost::mutex m_muxtimes;
                boost::mutex m_muxmemory;
                std::map< std::string, std::vector<unsigned long long> > m_times;
                std::map< std::string, std::vector<unsigned long long> > m_memory;
            
        };


    #endif

#endif

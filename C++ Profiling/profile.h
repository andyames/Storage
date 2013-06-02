#ifndef BENCHMARK

    #define PROFILE

#else
    
    #ifndef __PROFILE
    #define __PROFILE
    
        #define PROFILE   Benchmark l_benchmark__LINE__(__FUNCTION__);


        #include <map>
        #include <vector>
        #include <string>
        #include <numeric>
        #include <iostream>
        #include <stdexcept>
        #include <boost/thread.hpp>
        #include <boost/foreach.hpp>
        #include "benchmark.h"
        //#include <boost/shared_ptr.hpp>



        class Profile
        {
            public :
            
                static void createInstance( void );
                static void releaseInstance( void );
                static Profile* getInstance( void );
            
                std::map<std::string, std::vector<unsigned long long> > getTimes( void ) const;
                std::map<std::string, std::vector<unsigned long long> > getMemory( void ) const;
                void setBenchmarkTime( const std::string&, const unsigned long long& ); 
            
                //void setBenchmarkMemory( const std::string& p_name, ??? )
                //boost::shared_ptr<Benchmark> benchmark( const std::string& ) const;
                
            
                friend std::ostream& operator<< ( std::ostream&, const Profile& );

            
            
            
            private :
                
                Profile( void ) : m_muxtimes(), m_muxmemory(), m_times(), m_memory() {};
                ~Profile( void ) {};
                Profile( const Profile& ) {};
                Profile& operator=( const Profile& );
            
                static void AverageDerivationMedian( const std::vector<unsigned long long>&, double&, double&, unsigned long long& );
            
                static Profile* m_instance;

                boost::mutex m_muxtimes;
                boost::mutex m_muxmemory;
                std::map< std::string, std::vector<unsigned long long> > m_times;
                std::map< std::string, std::vector<unsigned long long> > m_memory;
            
        };

    #endif

#endif

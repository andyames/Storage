#ifndef BENCHMARK

    #define PROFILING
    #define PROFILINGINIT
    #define PROFILINGCLOSE
    #define PROFILINGINSTANCE ""
    #define PROFILINGDEFINITION

#else
    
    #ifndef __PROFILE
    #define __PROFILE
    
        #define PROFILING            Benchmark l_benchmark__LINE__(__FUNCTION__);
        #define PROFILING_NAME(name) Benchmark l_benchmark__LINE__(name);

        

        #define PROFILINGINIT Profile::createInstance();
        #define PROFILINGCLOSE Profile::releaseInstance();
        #define PROFILINGINSTANCE *Profile::getInstance()
        #define PROFILINGDEFINITION Profile* Profile::m_instance = NULL;


        #include <map>
        #include <string>
        #include <vector>
        #include <numeric>
        #include <sstream>
        #include <iostream>
        #include <stdexcept>
        #include <boost/thread.hpp>
        #include <boost/foreach.hpp>

        #include "benchmark.h"



        class Profile
        {
            public :
            
                static void createInstance( void );
                static void releaseInstance( void );
                static Profile* getInstance( void );
            
                std::map<std::string, std::vector<unsigned long long> > getTimes( void ) const;
                std::map<std::string, std::vector<unsigned long long> > getMemory( void ) const;
                void setBenchmarkTime( const std::string&, const unsigned long long& ); 
            
                friend std::ostream& operator<< ( std::ostream&, const Profile& );

            
            
            
            private :
                
                Profile( void ) : m_muxtimes(), m_muxmemory(), m_times(), m_memory() {};
                ~Profile( void ) {};
                Profile( const Profile& ) {};
                Profile& operator=( const Profile& );
            
                template<typename T> static std::string convert( const T& );
                template<typename T, typename L> static void AverageDerivationMedian( const std::vector<T>&, L&, L&, T& );
                static std::string repeat( const std::size_t&, const std::string& = " " );
            
                static Profile* m_instance;

                boost::mutex m_muxtimes;
                boost::mutex m_muxmemory;
                std::map< std::string, std::vector<unsigned long long> > m_times;
                std::map< std::string, std::vector<unsigned long long> > m_memory;
            
        };



        template<typename T, typename L> inline void Profile::AverageDerivationMedian( const std::vector<T>& p_vec, L& p_average, L& p_stdderivation, T& p_median )
        {
            L sum      = static_cast<L>(0);
            BOOST_FOREACH( L d, p_vec )
                sum   += d;
            p_average =  sum / p_vec.size();
            
            L accum    = static_cast<L>(0);
            //Lambda call - only with  C++0x: std::for_each(p_vec.begin(), p_vec.end(), [&accum](const double& d) { accum += (d - p_average) * (d - p_average); });
            BOOST_FOREACH( L d, p_vec )
                accum += (d - p_average) * (d - p_average);
                
            p_stdderivation = sqrt(accum / (p_vec.size()-1));
            p_median        = p_vec[(p_vec.size()-1)/2];
        }

        template<typename T> inline std::string Profile::convert( const T& p_in )
        {
            std::ostringstream os;
            os << p_in;
            return os.str();
        }

    #endif

#endif

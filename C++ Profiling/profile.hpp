#ifndef PROFILING

    #define PROFILE

#else

    #define PROFILE Benchmark l_benchmark( __FUNCTION __ );


    #include <string>
    #include <iostream>



    class Benchmark
    {
        public :
            
            Benchmark( const std::string& p_functionname ) : m_functionname(p_functionname) {};
        
            friend std::ostream& operator<< ( std::ostream& p_stream, const Benchmark& p )
            {
                p_stream << p.m_functionname << "\t" << (m_endtime-m_starttime) << std::endl;
                return p_stream;
            };
        
        
        private :
            
            const std::string m_functionname;
        
            unsigned long long m_starttime;
            
            unsigned long long m_endtime;
        
    };

#endif
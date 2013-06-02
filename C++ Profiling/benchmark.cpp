#include "benchmark.h"

Benchmark::Benchmark( const std::string& p_functionname ) : 
    m_functionname(p_functionname), 
    m_starttime(getCycles())
{};

Benchmark::~Benchmark( void )
{
    m_endtime = getCycles();
    Profile::getInstance()->setBenchmarkTime( m_functionname, m_endtime-m_starttime);
};



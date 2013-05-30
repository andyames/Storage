
#include <iostream>
#include "profile.hpp"


void func(void)
{
    #PROFILE
    
    for(std::size_t i=0; i < 100000; ++i)
        ;
}



int main(int p_argc, char* p_argv[])
{
    #PROFILE
    func();
    std::cout << *Profile::getInstance() << std::endl;
}
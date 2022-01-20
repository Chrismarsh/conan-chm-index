// Modification of http://viennacl.sourceforge.net/doc/examples_2tutorial_2libviennacl_8cpp-example.html

#include <iostream>
#include <vector>

#include <viennacl/vector.hpp>


int main(int argc, char* argv[])
{
    std::size_t size = 10;


    viennacl::vector<float> host_x = viennacl::scalar_vector<float>(size, 1.0, viennacl::context(viennacl::MAIN_MEMORY));
    viennacl::vector<float> host_y = viennacl::scalar_vector<float>(size, 2.0, viennacl::context(viennacl::MAIN_MEMORY));

    std::cout << " --- Host ---" << std::endl;
    std::cout << "host_x: " << host_x << std::endl;
    std::cout << "host_y: " << host_y << std::endl;

	return 0;
}
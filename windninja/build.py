from cpt.packager import ConanMultiPackager
from collections import defaultdict
import os

if __name__ == "__main__":
    builder = ConanMultiPackager(cppstds=[14],
                                archs=["x86_64"],
                                build_types=["Release"],
                                build_policy='missing')
                        
    builder.add_common_builds(pure_c=False, shared_option_name=False)
    builder.remove_build_if(lambda build: build.settings["compiler.libcxx"] == "libstdc++") # old ABI

    #building in the CI disable the omp build of Windninja because of weirndess with the arm64/64 libomp
    builder.update_build_if(lambda build: os.environ['CI'], new_options={'windninja:openmp': False})


    builder.run()


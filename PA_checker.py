################### grid ####################
# CSCI 180 Summer 2023 Programming Assignment #
#############################################

# The script cannot run in Windows
import subprocess, threading
import os, signal, sys

python_executable = 'python3 '
cpp_compile_flags = '-std=c++17'
time_limit = 3


class Command:
    def __init__(self):
        self.process = None

    def run(self, cmd, timeout=60):
        def target():
            self.process = subprocess.Popen(cmd, shell=True, preexec_fn=os.setsid)
            self.process.communicate()

        thread = threading.Thread(target=target)
        thread.start()

        thread.join(timeout)
        if thread.is_alive():
            os.killpg(self.process.pid, signal.SIGTERM)
            thread.join()
            return (1, "Time Limit Exceeded")
        if self.process.returncode == 0:
            return (0, "Program exited with return value 0")
        return (2, "Runtime Error")


cs = Command()


def run_tests(cmd, test_dir, method_python):
    count = 0
    pass_count = 0
    tle_count = 0
    re_count = 0
    wa_count = 0
    log_name = test_dir + f"/auto_log_py.txt" if method_python else test_dir + f"/auto_log_cpp.txt"
    fres = open(log_name, "w")
    for cond in ['true', 'false']:
        # filter out those end with '_out.txt'
        files = [f for f in os.listdir("./tests/" + cond) if not f.endswith('_out.txt')]
        for file in files:
            path = file.split('.')
            ext = path[-1]
            if ext != "txt":
                continue
            count += 1
            name = ".".join(path[0:-1])
            print(count, "Running: " + name)
            (res, desc) = cs.run(cmd + " ./tests/" + cond + "/" + name + ".txt", time_limit)
            if res == 1:
                tle_count += 1
                fres.write(name + ": Time Limit Exceeded (Terminated)\n")
            elif res == 2:
                re_count += 1
                fres.write(name + ": Runtime Error (Return value is not 0)\n")
            else:
                fin = open("./tests/" + cond + "/" + name + "_out.txt", "r")
                output = fin.readline()
                fin.close()
                try:
                    output = int(output)
                    _cond = (cond == 'true')
                    if output == int(_cond):
                        pass_count += 1
                        fres.write(name + ": Correct Answer!\n")
                    else:
                        wa_count += 1
                        fres.write(name + ": Incorrect Answer!\n")
                except Exception as e:
                    wa_count += 1
                    fres.write(name + str(e) + ": Unrecognized Output Format\n")

    fres.write("=========== Summary ==========\n")
    fres.write("Passed " + str(pass_count) + " / " + str(count) + " test cases.\n")
    if (pass_count == count):
        fres.write("All test cases passed: Accepted!\n")
    fres.close()
    print("Passed " + str(pass_count) + " / " + str(count) + " test cases.")
    print("Results saved to " + test_dir)

    return (pass_count == count), pass_count, count


def run_py_tests(test_dir):
    print("Found python solution, start grading...")
    return run_tests(python_executable + test_dir + "/kill_Down_with_Trojans.py", test_dir, True)


def run_cpp_tests(test_dir):
    print("Found C++ solution, compiling...")
    (res, desc) = cs.run("g++ " + test_dir + "/kill_Down_with_Trojans.cpp" + " -o " + test_dir + "/kill_Down_with_Trojans" + " " + cpp_compile_flags)
    if res != 0:
        print("Failed to compile source code: " + desc)
        return False, -1, -1
    return run_tests(test_dir + "/./kill_Down_with_Trojans", test_dir, False)


def run_grid(test_dir):
    any_correct = False
    if os.path.exists(test_dir + "/kill_Down_with_Trojans.py"):
        res_py = run_py_tests(test_dir)
        any_correct = any_correct or res_py[0]
    if os.path.exists(test_dir + "/kill_Down_with_Trojans.cpp"):
        res_c = run_cpp_tests(test_dir)
        any_correct = any_correct or res_c[0]

        if any_correct:
            print("At least one correct solution found.")
            return True


if __name__ == "__main__":
    # TODO: change this to your repo directory;
    #       it's recommended to use absolute path
    your_repo_dir = "/Users/meech/Documents/GitHub/CS180-Programming-Assignment"
    run_grid(your_repo_dir)


import sys, os

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f'Usage:python timer_for_testing_launch_and_stop.py <delay> <count>')
        sys.exit(1)
    delay = sys.argv[1]
    count = sys.argv[2]
    print(f'...sleeping for {delay} seconds for {count} times')
    for i in range(int(count)):
        print(f'...sleeping for {delay} seconds')
        os.system(f'sleep {delay}')
        print(f'just paused for iteration {i + 1}')

import HelpFunctions as Functions


def p(x):
    return x**2

res = []
if __name__ == '__main__':

    executor = Functions.get_thread_pool_executor(1)
    res.append(executor.submit(p, 5))
    executor.shutdown(wait=True)
    print(res[0].result())
import Queue
import itertools
import string

# Globals:
RANGE_LENGTH = 100000
PASSWORD_LENGTH = 4

password_generator = itertools.product(string.ascii_lowercase, repeat=PASSWORD_LENGTH)
password_generator_empty = False
password_queue = Queue.Queue()


def _generate_range():
    """
    generate_range generate_range() -> tuple

    Generate range of passwords of certain length.
    """

    global password_generator
    global password_length
    global password_generator_empty

    try:

        # start position
        start = password_generator.next()

    except StopIteration:

        password_generator_empty = True

    else:

        for i in range(RANGE_LENGTH):

            try:
            	
            	# stop position
                # update every round in case of exception
                stop = password_generator.next()

            except StopIteration:
                
                password_generator_empty = True

        else:

            start = ''.join(start)
            stop = ''.join(stop)

            return start, stop


def init_password_queue():
    """
    init_password_queue init_password_queue() -> None

    Initialize the password_queue variable with all available
    ranges.
    """

    global password_queue
    global password_generator_empty

    while not password_generator_empty:

        new_range = _generate_range()
        
        if new_range:

            password_queue.put(new_range)

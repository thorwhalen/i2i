
def simple_fixed_step_chunker(seq, chk_size, chk_step=None):
    """
      a function to get (an iterator of) segments [bt, tt) of chunks from an seqquence seq
      of size chk_size, with a step of chk_step

      :param seq: sequence of elements
      :param chk_size: length of the chunks
      :param chk_step: step between chunks
      :return: an iterator of the chunks

       """

    chk_step = chk_step or chk_size
    seq_minus_chk_length = len(seq) - chk_size
    for bt in range(0, seq_minus_chk_length, chk_step):
        yield seq[bt:(bt + chk_size)]
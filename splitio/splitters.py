"""A module for implementation of the Splitter engine"""
from __future__ import absolute_import, division, print_function, unicode_literals


from splitio.treatments import CONTROL
from splitio.hashfns import get_hash_fn


class Splitter(object):
    """
    The class responsible for selecting a treatment given a key, a feature seed and condition
    partitions.
    """
    def get_treatment(self, key, seed, partitions, algo):
        """
        Returs a treatment for a key, a feature seed and condition partitions. It returns CONTROL
        if partitions is None or empty.
        :param key: The key for which to determine the treatment
        :type key: str
        :param seed: The feature seed
        :type seed: int
        :param partitions: The condition partitions
        :type partitions: list
        :return: The treatment
        :rtype: str
        """
        if not partitions:
            return CONTROL

        if len(partitions) == 1 and partitions[0].size == 100:
            return partitions[0].treatment

        hashfn = get_hash_fn(algo)
        return self.get_treatment_for_bucket(
            self.get_bucket(hashfn(key, seed)),
            partitions
        )

    def get_bucket(self, key_hash):
        """
        Get the bucket for a key hash
        :param key_hash: The hash for a key
        :type key_hash: int
        :return: The bucked for a hash
        :rtype: int
        """
        return abs(key_hash) % 100 + 1

    def get_treatment_for_bucket(self, bucket, partitions):
        """
        Gets the treatment for a given bucket and partitions. It'll return treatment for the first
        partition that contains the bucket.
        :param bucket: The bucket number generated by get_bucket
        :type bucket: int
        :param partitions: The condition partitions
        :type partitions: list
        :return: The treatment
        :rtype: str
        """
        covered_buckets = 0

        for partition in partitions:
            covered_buckets += partition.size

            if covered_buckets >= bucket:
                return partition.treatment

        return CONTROL

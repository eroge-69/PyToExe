import os
import math
import time

from gmpy2 import gmpy2

class S:            # Scalar field
    N = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141
    N_2 = (N + 1) // 2          # 2**-1 mod N
    gmp_N = gmpy2.mpz(N)

    @staticmethod
    def add(a, b):
        return gmpy2.mod(gmpy2.add(a, b,), S.gmp_N)

    @staticmethod
    def mul(a, b):
        return gmpy2.mod(gmpy2.mul(a, b), S.gmp_N)


class F:        # Curve field
    P = 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f
    gmp_P = gmpy2.mpz(P)
    gmp_P4 = gmpy2.mpz((P + 1) // 4)

    @staticmethod
    def add(a, b):
        return gmpy2.mod(gmpy2.add(a, b), F.gmp_P)

    @staticmethod
    def mul(a, b):
        return gmpy2.mod(gmpy2.mul(a, b), F.gmp_P)

    @staticmethod
    def pow(b, e):
        return gmpy2.powmod(b, e, F.gmp_P)

    @staticmethod
    def sqrt(a):
        return gmpy2.powmod(a, F.gmp_P4, F.gmp_P)

    @staticmethod
    def inv(a):
        return gmpy2.invert(a, F.gmp_P)


class Point:            # Affine point
    def __init__(self, x, y, parity=-1):
        self.x = x
        self.y = y if parity == -1 else Point.calc_y(x, parity)

    @classmethod
    def uncompress(cls, s):
        parity, xh = int(s[:2], 16), s[2:]
        if parity not in [2, 3]:
            raise Exception("Expected parity 02 or 03")
        return Point(int(xh, 16), 0, parity % 2)

    @staticmethod
    def calc_y(x, parity):
        y = F.sqrt(F.add(F.pow(x, 3), 7))   # y = sqrt(x**3 + 7)
        return y if parity == y % 2 else F.P - y


class JPoint:           # Jacobian point
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def affine(self):
        z = F.inv(self.z)
        z2 = F.mul(z, z)
        return Point(F.mul(self.x, z2), F.mul(self.y, F.mul(z, z2)))

    def mul(self, n):
        if self.y == 0 or n == 0:
            return JPoint(0, 0, 1)

        if n == 1:
            return self

        if n < 0 or n >= S.N:
            return self.mul(n % S.N)

        if (n % 2) == 0:
            return self.mul(n // 2).double()

        return self.mul(n // 2).double().add(self)

    def double(self):
        if self.y == 0:
            return JPoint(0, 0, 0)

        y2 = F.mul(self.y, self.y)
        s = F.mul(4 * self.x, y2)
        n = F.mul(3 * self.x, self.x)

        x = F.add(F.mul(n, n), - 2 * s)
        return JPoint(x, F.add(F.mul(n, s - x), -F.mul(8 * y2, y2)), F.mul(2 * self.y, self.z))

    def add(self, q):
        if self.y == 0:
            return q
        if q.y == 0:
            return self

        qz2 = F.mul(q.z, q.z)
        pz2 = F.mul(self.z, self.z)
        u1 = F.mul(self.x, qz2)
        u2 = F.mul(q.x, pz2)
        s1 = F.mul(self.y, F.mul(q.z, qz2))
        s2 = F.mul(q.y, F.mul(self.z, pz2))

        if u1 == u2:
            if s1 != s2:
                return JPoint(0, 0, 1)
            return self.double()

        h = F.add(u2, -u1)
        r = F.add(s2, -s1)
        h2 = F.mul(h, h)
        h3 = F.mul(h, h2)
        u1h2 = F.mul(u1, h2)
        nx = F.add(F.mul(r, r), -F.add(h3, 2 * u1h2))
        ny = F.add(F.mul(r, F.add(u1h2, -nx)), -F.mul(s1, h3))
        nz = F.mul(h * self.z, q.z)

        return JPoint(nx, ny, nz)


class Group:
    G = Point(
        0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798,
        0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8
    )

    @staticmethod
    def add(p: Point, q: Point):
        if p.x == q.x:
            raise Exception('Point adding with same X not supported')

        m = F.mul(F.add(p.y, -q.y), F.inv(F.add(p.x, -q.x)))
        x = F.add(F.add(F.mul(m, m), -p.x), -q.x)
        return Point(x, F.add(F.mul(m, F.add(q.x, -x)), -q.y))

    @classmethod
    def mul(cls, p: Point, k):
        return JPoint(p.x, p.y, 1).mul(k).affine()

    @classmethod
    def batch_add(cls, ga, gb):
        n = len(ga)
        d = [0] * n
        p = [0] * n
        z = 1
        for i in range(n):
            d[i] = F.add(ga[i].x, -gb[i].x)
            z = F.mul(z, d[i])
            p[i] = z

        t = F.inv(z)

        for i in range(n - 1, -1, -1):
            if i > 0:
                xi = F.mul(t, p[i - 1])
                t = F.mul(t, d[i])
            else:
                xi = t

            m = F.mul(F.add(ga[i].y, -gb[i].y), xi)
            ga[i].x = F.add(F.add(F.mul(m, m), -ga[i].x), -gb[i].x)
            ga[i].y = F.add(F.mul(m, F.add(gb[i].x, -ga[i].x)), -gb[i].y)


class TrueRandom:
    def __init__(self, max_value: int, num_bits: int, min_value: int = 0):
        self.upper_bound = max_value - min_value + 1
        self.min = min_value
        self.num_bits = num_bits
        self.domain = 2 ** num_bits
        self.num_bytes = math.ceil(num_bits / 8)
        self.shift = 8 * self.num_bytes - num_bits

    def get_next(self):
        random_bytes = os.urandom(self.num_bytes)

        # trim to num_bits
        random_int = int.from_bytes(random_bytes, byteorder='big') >> self.shift

        # normalize from domain range to target range
        sample = self.upper_bound * random_int // self.domain

        return sample + self.min


class Kangaroo:
    def __init__(self, k1: int, k2: int, dp: int, herd_size: int,
                 verify: bool = False):
        self.key_offset = k1

        b = k2 - k1 + 1
        # subtract k1 to search in [0, b) interval
        k2 -= k1
        k1 = 0

        self.k1 = k1
        self.k2 = k2
        self.b = b
        self.dp = dp
        self.herd_size = herd_size
        self.verify = verify

        self.m = herd_size + herd_size               # m/2 + m/2

        # compute optimal alpha for minimum expected total group operations
        # numJumps(a) = (b/4a + 4a/m**2) * m; minimal when a = m * sqrt(b)/4
        alpha = herd_size * math.sqrt(b) / 2

        self.jump_distances, self.jump_points, _ = self.build_jump_distances(alpha, with_points=True)
        self.n = len(self.jump_distances)

        # ensure we'll never stumble a kang onto a jump point (erase doubling branch)
        self.key_offset -= (2 ** (self.n + 10) + 1)
        self.k1 += (2 ** (self.n + 10) + 1)
        self.k2 += (2 ** (self.n + 10) + 1)

        self.alpha_real = sum(self.jump_distances) / self.n

        # adjust alpha to the actual average jump distance
        self.alpha_expected = alpha

        # (b/(4m * sqrt(b)/4) + 4(m * sqrt(b)/4)/m**2) * m == 2 sqrt(b)
        self.expected_total_jumps = 2 * math.sqrt(b)

        # set v to the "partition" size for a processor, and not a power of two
        # v = b // m - 1                          # (b/2) / (m/2)
        self.v = 37

        # DP overhead assuming we jump all herds at once, at every step
        self.expected_total_jumps += (1 << self.dp) * self.m
        self.avg_jumps_per_kang = self.expected_total_jumps / self.m

        self.hashmap = {}

        self.tames: list[Point | None] = [None] * herd_size
        self.t_dist = [0] * herd_size

        self.wilds: list[Point | None] = [None] * herd_size
        self.w_dist = [0] * herd_size

        self.P = self.P_neg = None
        self.num_created = 0

        self.batch_jp: list = [None] * herd_size     # buffer for batched group operations

    def solve(self, target_point: Point):
        # shift P to the left to bring DLP in search interval
        target_point = Group.add(target_point, Group.mul(Group.G, -self.key_offset))
        self.P = target_point

        self.num_created = 0
        self.hashmap.clear()
        k_cand, counter, tbl_size = self.kangaroo()

        failed = self.verify
        for i in range(len(k_cand)):
            if failed:
                q = Group.mul(Group.G, k_cand[i])
                if q.x == self.P.x and q.y == self.P.y:
                    failed = False
                    print(f'Private Key: {hex(S.add(k_cand[i], self.key_offset))}')
            k_cand[i] = S.add(k_cand[i], self.key_offset)

        if failed:
            raise Exception(f'Solution verify failed!\n{k_cand}')

        return k_cand, counter, tbl_size

    def create_kangaroo(self, kang_type, pos: int, v: int):
        k1, k2 = self.k1, self.k2

        if kang_type == 0:
            d = self.b // 2 + pos * v                       # b/2 + i * v

            self.t_dist[pos] = d
            self.tames[pos] = Group.mul(Group.G, k1 + d)
        else:
            d = pos * v                                     # 0 + i * v

            self.w_dist[pos] = d
            self.wilds[pos] = Group.add(self.P, Group.mul(Group.G, d))

    def check_col(self, kang_type, pos, dp_mask):
        k1, k2, hashmap = self.k1, self.k2, self.hashmap

        if kang_type == 0:
            herd, dist = self.tames, self.t_dist
        else:
            herd, dist = self.wilds, self.w_dist

        x = herd[pos].x     # shift >> 192 too expensive in Python

        if (x & dp_mask) == 0:
            item = hashmap.get(x)

            if item is not None:
                if item[0] != kang_type:
                    # collision
                    d_wild, d_tame = (item[1], dist[pos]) if kang_type == 0 else (dist[pos], item[1])
                    # k1 + tameDist == k + wildDist
                    return [
                        S.add(k1 + d_tame, -d_wild),        # k1 + t = k + w            (k > 0)
                    ], 0
                else:
                    # move forward
                    d = 7
                    dist[pos] += d
                    herd[pos] = Group.add(herd[pos], Group.mul(Group.G, d))

                    # this will recurse until a non-dead kangaroo is produced
                    k, created = self.check_col(kang_type, pos, dp_mask)
                    self.num_created += created
                    return k, 1 + created
            else:
                hashmap[x] = kang_type, dist[pos]

        return 0, 0

    @staticmethod
    def build_jump_distances(alpha, with_points=False):
        jump_points_fwd = None
        jump_points_bwd = None
        jump_distances = []

        # compute |A| as powers of two for all elements but the last
        # and adjust the last element so that avg(A) == alpha
        r = 0
        s = 0
        while True:
            jump_distance = 2 ** r
            s += jump_distance
            r += 1
            a = s / r
            if a < alpha:
                jump_distances.append(jump_distance)
            else:
                total = s - jump_distance
                last_dist = int(alpha * r - total)
                jump_distances.append(last_dist)
                break

        if with_points:
            jump_points_fwd, jump_points_bwd = Kangaroo.create_jump_points(jump_distances)

        return jump_distances, jump_points_fwd, jump_points_bwd

    @staticmethod
    def create_jump_points(jump_distances: list, base_p = Group.G):
        jump_points_fwd = []
        jump_points_bwd = []

        for dist in jump_distances:
            q = Group.mul(base_p, dist)
            jump_points_fwd.append(q)
            jump_points_bwd.append(Point(q.x, F.P - q.y))

        return jump_points_fwd, jump_points_bwd

    def kangaroo(self):
        k1, k2, dp, herd_size = self.k1, self.k2, self.dp, self.herd_size

        print(
            f'            kangaroos (m): {self.m}'
            f'\n      jump distances |A|: {self.n}'
            f'\n        avg jumps / kang: {self.avg_jumps_per_kang:.0f}'
            f'\n    expected total jumps: {self.expected_total_jumps:20.0f} {math.log2(self.expected_total_jumps):.2f} bits'
            f'\n avg ideal jump distance: {self.alpha_expected:20.0f} {math.log2(self.alpha_expected):.2f} bits'
            f'\n  avg real jump distance: {self.alpha_real:20.0f} {math.log2(self.alpha_real):.2f} bits'
        )

        batch_jp = self.batch_jp
        num_ops = 0
        dp_mask = (1 << dp) - 1

        for idx in range(herd_size):
            self.create_kangaroo(0, idx, self.v)
            self.create_kangaroo(1, idx, self.v)
            self.num_created += 2

        tames, t_dist = self.tames, self.t_dist
        wilds, w_dist = self.wilds, self.w_dist
        n = self.n

        start_time = time.time()
        last_p_time = 0

        while True:
            for idx in range(herd_size):
                k, born = self.check_col(0, idx, dp_mask)
                self.num_created += born
                if k:
                    return k, num_ops, len(self.hashmap)

                jump_idx = tames[idx].x % n
                # tames[idx] = Group.add(tames[idx], jump_points[d])        # un-batched addition
                batch_jp[idx] = self.jump_points[jump_idx]
                t_dist[idx] += self.jump_distances[jump_idx]

            Group.batch_add(tames, batch_jp)
            num_ops += len(tames)

            for idx in range(herd_size):
                k, born = self.check_col(1, idx, dp_mask)
                self.num_created += born
                if k:
                    return k, num_ops, len(self.hashmap)

                jump_idx = wilds[idx].x % n
                # wilds[idx] = Group.add(wilds[idx], jump_points[d])        # un-batched addition
                batch_jp[idx] = self.jump_points[jump_idx]
                w_dist[idx] += self.jump_distances[jump_idx]

            Group.batch_add(wilds, batch_jp)
            num_ops += len(wilds)

            total_time = time.time() - start_time
            if total_time - last_p_time > 2:
                last_p_time = total_time
                print(f'Ops: {num_ops} Table size: {len(self.hashmap)} Speed: {num_ops / total_time:.0f} ops/s')


def benchmark_kangaroo(bits: int, dp: int = 0, herd_size: int = 128, num_runs=100):
    k1, k2 = 1, 1 << bits       # k interval = [1, 2**n]
    total_group_add = 0         # group operations (e.g. P + Q)
    total_group_mul = 0         # point scalar ops (e.g. [k] * P)
    total_size = 0
    total_time = 0
    tr = TrueRandom(k2, 256, k1)
    kangaroo = Kangaroo(k1, k2, dp, herd_size, verify=True)

    for i in range(num_runs):
        pk = tr.get_next()
        print(f'Solve for {pk}')
        target_point = Group.mul(Group.G, pk)

        start_time = time.monotonic()
        k, ops, hashmap_size = kangaroo.solve(target_point)
        total_time += time.monotonic() - start_time

        found = False
        for k_cand in k:
            if k_cand == pk:
                found = True
                break

        if not found:
            raise Exception(f'BAD solution! {pk} not in {k}')

        total_group_mul += kangaroo.num_created
        total_group_add += ops
        total_size += hashmap_size

        ops_per_solve = total_group_add / (i + 1)
        dp_ovh = (1 << dp) * herd_size
        ops_minus_dp_overhead = ops_per_solve - dp_ovh
        print(f'[{i + 1}] AVG Ops: {ops_per_solve:.0f}'
              f' ({ops_minus_dp_overhead / math.sqrt(k2 - k1 + 1):.3f} * sqrt(b)'
              f' + (dp_ovh = 2**{math.log2(dp_ovh)}))'
              f' AVG Stored: {total_size / (i + 1):.0f}'
              f' AVG k_crt: {total_group_mul / (i + 1):.0f}'
              f' AVG Speed: {total_group_add / total_time:.0f} op/s'
              )


def run_puzzle(idx: int, pub_key, dp: int = 0, herd_size: int = 128):
    # puzzle #X has (X - 1) unknown bits
    k1 = 1 << (idx - 1)
    k2 = (k1 << 1) - 1
    target_point = Point.uncompress(pub_key)

    k = Kangaroo(k1, k2, dp, herd_size, verify=True)
    start_time = time.monotonic()
    _, ops, hashmap_size = k.solve(target_point)
    total_time = time.monotonic() - start_time

    print(f'Ops: {ops} Stored: {hashmap_size}'
          f'\nSpeed: {ops / total_time:.0f} ops/s'
          f'\nFinished in {total_time:.3} s'
          )


if __name__ == '__main__':
     run_puzzle(32, '0209c58240e50e3ba3f833c82655e8725c037a2294e14cf5d73a5df8d56159de69',
                herd_size=7)

     run_puzzle(33, '03a355aa5e2e09dd44bb46a4722e9336e9e3ee4ee4e7b7a0cf5785b283bf2ab579',
               herd_size=13, dp=3)
               
     run_puzzle(66, '024ee2be2d4e9f92d2f5a4a03058617dc45befe22938feed5b7a6b7282dd74cbdd',
               herd_size=52, dp=3)
               
    # run_puzzle(66, '024ee2be2d4e9f92d2f5a4a03058617dc45befe22938feed5b7a6b7282dd74cbdd',
         #    herd_size=43, dp=9)

    #run_puzzle(135, '02145d2611c823a396ef6712ce0f712f09b9b4f3135e3e0aa3230fb9b6d08d1e16',
    #           herd_size=92160, dp=20)

    # benchmark_kangaroo(32, dp=4, herd_size=512, num_runs=1000)

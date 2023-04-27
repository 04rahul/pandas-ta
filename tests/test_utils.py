# -*- coding: utf-8 -*-
from email.policy import default
from unittest import TestCase, skip

import numpy as np
import numpy.testing as npt
from pandas import DataFrame, Series
from pandas.api.types import is_datetime64_ns_dtype, is_datetime64tz_dtype

from pandas_ta.performance import percent_return
from pandas_ta.utils import sample as pta_sample

from .config import sample_data
from .context import pandas_ta


data = {
    "zero": [0, 0],
    "a": [0, 1],
    "b": [1, 0],
    "c": [1, 1],
    "crossed": [0, 1],
}


class TestUtilities(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.data = sample_data

    @classmethod
    def tearDownClass(cls):
        del cls.data

    def setUp(self):
        self.crosseddf = DataFrame(data)
        self.utils = pandas_ta.utils

    def tearDown(self):
        del self.crosseddf
        del self.utils

    def test__add_prefix_suffix(self):
        result = self.data.ta.hl2(prefix="pre")
        self.assertEqual(result.name, "pre_HL2")

        result = self.data.ta.hl2(suffix="suf")
        self.assertEqual(result.name, "HL2_suf")

        result = self.data.ta.hl2(prefix="pre", suffix="suf")
        self.assertEqual(result.name, "pre_HL2_suf")

        result = self.data.ta.hl2(prefix=1, suffix=2)
        self.assertEqual(result.name, "1_HL2_2")

        result = self.data.ta.macd(prefix="pre", suffix="suf")
        for col in result.columns:
            self.assertTrue(col.startswith("pre_") and col.endswith("_suf"))

    @skip
    def test__above_below(self):
        result = self.utils._above_below(self.crosseddf["a"], self.crosseddf["zero"], above=True)
        self.assertIsInstance(result, Series)
        self.assertEqual(result.name, "a_A_zero")
        npt.assert_array_equal(result, self.crosseddf["c"])

        result = self.utils._above_below(self.crosseddf["a"], self.crosseddf["zero"], above=False)
        self.assertIsInstance(result, Series)
        self.assertEqual(result.name, "a_B_zero")
        npt.assert_array_equal(result, self.crosseddf["b"])

        result = self.utils._above_below(self.crosseddf["c"], self.crosseddf["zero"], above=True)
        self.assertIsInstance(result, Series)
        self.assertEqual(result.name, "c_A_zero")
        npt.assert_array_equal(result, self.crosseddf["c"])

        result = self.utils._above_below(self.crosseddf["c"], self.crosseddf["zero"], above=False)
        self.assertIsInstance(result, Series)
        self.assertEqual(result.name, "c_B_zero")
        npt.assert_array_equal(result, self.crosseddf["zero"])

    def test_above(self):
        result = self.utils.above(self.crosseddf["a"], self.crosseddf["zero"])
        self.assertIsInstance(result, Series)
        self.assertEqual(result.name, "a_A_zero")
        npt.assert_array_equal(result, self.crosseddf["c"])

        result = self.utils.above(self.crosseddf["zero"], self.crosseddf["a"])
        self.assertIsInstance(result, Series)
        self.assertEqual(result.name, "zero_A_a")
        npt.assert_array_equal(result, self.crosseddf["b"])

    def test_above_value(self):
        result = self.utils.above_value(self.crosseddf["a"], 0)
        self.assertIsInstance(result, Series)
        self.assertEqual(result.name, "a_A_0")
        npt.assert_array_equal(result, self.crosseddf["c"])

        result = self.utils.above_value(self.crosseddf["a"], self.crosseddf["zero"])
        self.assertIsNone(result)

    def test_below(self):
        result = self.utils.below(self.crosseddf["zero"], self.crosseddf["a"])
        self.assertIsInstance(result, Series)
        self.assertEqual(result.name, "zero_B_a")
        npt.assert_array_equal(result, self.crosseddf["c"])

        result = self.utils.below(self.crosseddf["zero"], self.crosseddf["a"])
        self.assertIsInstance(result, Series)
        self.assertEqual(result.name, "zero_B_a")
        npt.assert_array_equal(result, self.crosseddf["c"])

    def test_below_value(self):
        result = self.utils.below_value(self.crosseddf["a"], 0)
        self.assertIsInstance(result, Series)
        self.assertEqual(result.name, "a_B_0")
        npt.assert_array_equal(result, self.crosseddf["b"])

        result = self.utils.below_value(self.crosseddf["a"], self.crosseddf["zero"])
        self.assertIsNone(result)

    def test_combination(self):
        """Utility[Math]: Combination"""
        self.assertIsNotNone(self.utils.combination())

        self.assertEqual(self.utils.combination(), 1)
        self.assertEqual(self.utils.combination(r=-1), 1)

        self.assertEqual(self.utils.combination(n=10, r=4, repetition=False), 210)
        self.assertEqual(self.utils.combination(n=10, r=4, repetition=True), 715)

    def test_cross_above(self):
        result = self.utils.cross(self.crosseddf["a"], self.crosseddf["b"])
        self.assertIsInstance(result, Series)
        npt.assert_array_equal(result, self.crosseddf["crossed"])

        result = self.utils.cross(self.crosseddf["a"], self.crosseddf["b"], above=True)
        self.assertIsInstance(result, Series)
        npt.assert_array_equal(result, self.crosseddf["crossed"])

        result = self.utils.cross(self.crosseddf["a"], self.crosseddf["b"], equal=False)
        self.assertIsInstance(result, Series)
        npt.assert_array_equal(result, self.crosseddf["crossed"])

    def test_cross_below(self):
        result = self.utils.cross(self.crosseddf["b"], self.crosseddf["a"], above=False)
        self.assertIsInstance(result, Series)
        npt.assert_array_equal(result, self.crosseddf["crossed"])

        result = self.utils.cross(self.crosseddf["a"], self.crosseddf["b"], above=False)
        self.assertFalse(result[0])

        result = self.utils.cross(self.crosseddf["b"], self.crosseddf["a"], above=False, equal=False)
        self.assertIsInstance(result, Series)
        npt.assert_array_equal(result, self.crosseddf["crossed"])

    def test_df_dates(self):
        """Utility[Date]: DF Dates"""
        result = self.utils.df_dates(self.data)
        self.assertEqual(None, result)

        # result = self.utils.df_dates(self.data, "1999-11-01")
        # self.assertEqual(1, result.shape[0])

        # result = self.utils.df_dates(self.data, ["1999-11-01", "2020-08-15", "2020-08-24", "2020-08-25", "2020-08-26", "2020-08-27"])
        # self.assertEqual(5, result.shape[0])

        # result = self.utils.df_dates(self.data, ["1999-11-01", "2000-03-15"])
        # self.assertEqual(2, result.shape[0])

    @skip
    def test_df_month_to_date(self):
        """Utility[Date]: MTD"""
        result = self.utils.df_month_to_date(self.data)

    @skip
    def test_df_quarter_to_date(self):
        """Utility[Date]: QTD"""
        result = self.utils.df_quarter_to_date(self.data)

    @skip
    def test_df_year_to_date(self):
        """Utility[Date]: YTD"""
        result = self.utils.df_year_to_date(self.data)

    def test_fibonacci(self):
        """Utility[Math]: Fibonacci"""
        self.assertIs(type(self.utils.fibonacci(zero=True, weighted=False)), np.ndarray)

        npt.assert_array_equal(self.utils.fibonacci(zero=True), np.array([0, 1, 1]))
        npt.assert_array_equal(self.utils.fibonacci(zero=False), np.array([1, 1]))

        npt.assert_array_equal(self.utils.fibonacci(n=0, zero=True, weighted=False), np.array([0]))
        npt.assert_array_equal(self.utils.fibonacci(n=0, zero=False, weighted=False), np.array([1]))

        npt.assert_array_equal(self.utils.fibonacci(n=5, zero=True, weighted=False), np.array([0, 1, 1, 2, 3, 5]))
        npt.assert_array_equal(self.utils.fibonacci(n=5, zero=False, weighted=False), np.array([1, 1, 2, 3, 5]))

    def test_fibonacci_weighted(self):
        """Utility[Math]: Fibonacci Weighted"""
        self.assertIs(type(self.utils.fibonacci(zero=True, weighted=True)), np.ndarray)
        npt.assert_array_equal(self.utils.fibonacci(n=0, zero=True, weighted=True), np.array([0]))
        npt.assert_array_equal(self.utils.fibonacci(n=0, zero=False, weighted=True), np.array([1]))

        npt.assert_allclose(self.utils.fibonacci(n=5, zero=True, weighted=True), np.array([0, 1 / 12, 1 / 12, 1 / 6, 1 / 4, 5 / 12]))
        npt.assert_allclose(self.utils.fibonacci(n=5, zero=False, weighted=True), np.array([1 / 12, 1 / 12, 1 / 6, 1 / 4, 5 / 12]))

    def test_geometric_mean(self):
        """Utility[Stats]: Geometric Mean"""
        returns = percent_return(self.data.close)
        result = self.utils.geometric_mean(returns)
        # result = geometric_mean(returns)
        self.assertIsInstance(result, (float, int))

        result = self.utils.geometric_mean(Series([12, 14, 11, 8]))
        # result = geometric_mean(Series([12, 14, 11, 8]))
        self.assertIsInstance(result, float)

        result = self.utils.geometric_mean(Series([100, 50, 0, 25, 0, 60]))
        # result = geometric_mean(Series([100, 50, 0, 25, 0, 60]))
        self.assertIsInstance(result, float)

        series = Series([0, 1, 2, 3])
        result = self.utils.geometric_mean(series)
        # result = geometric_mean(series)
        self.assertIsInstance(result, float)

        result = self.utils.geometric_mean(-series)
        # result = geometric_mean(-series)
        self.assertIsInstance(result, int)
        self.assertAlmostEqual(result, 0)

    def test_get_time(self):
        """Utility[Time]: Get Time"""
        result = self.utils.get_time(to_string=True)
        self.assertIsInstance(result, str)

        result = self.utils.get_time("NZSX", to_string=True)
        self.assertTrue("NZSX" in result)
        self.assertIsInstance(result, str)

        result = self.utils.get_time("SSE", to_string=True)
        self.assertIsInstance(result, str)
        self.assertTrue("SSE" in result)

    def test_hpoly(self):
        """Utility[Math]: Horners Polynomial"""
        self.assertEqual(self.utils.hpoly([1], 1), 1)
        self.assertEqual(self.utils.hpoly([1, 1], 1), 2)
        self.assertEqual(self.utils.hpoly([1, 0, -1], 1), 0)
        self.assertEqual(self.utils.hpoly([1, 0, 1], 1), 2)
        self.assertEqual(self.utils.hpoly([1, 1, 1], 1), 3)

    def test_inv_norm(self):
        """Utility[Stats]: Inverse Normal"""
        np.testing.assert_equal(self.utils.inv_norm(-0.01), np.nan)
        self.assertEqual(self.utils.inv_norm(0), -np.infty)
        self.assertEqual(self.utils.inv_norm(1 - 0.96), -1.7506860712521692)
        self.assertAlmostEqual(self.utils.inv_norm(1 - 0.8646), -1.101222112591979)
        self.assertEqual(self.utils.inv_norm(0.5), 0)
        self.assertAlmostEqual(self.utils.inv_norm(0.8646), 1.101222112591979)
        self.assertEqual(self.utils.inv_norm(0.96), 1.7506860712521692)
        self.assertEqual(self.utils.inv_norm(1), np.infty)
        np.testing.assert_equal(self.utils.inv_norm(1.01), np.nan)

    def test_linear_regression(self):
        """Utility[Math]: Linear Regression"""
        x = Series([1, 2, 3, 4, 5])
        y = Series([1.8, 2.1, 2.7, 3.2, 4])

        result = self.utils.linear_regression(x, y)
        self.assertIsInstance(result, dict)
        self.assertIsInstance(result["a"], float)
        self.assertIsInstance(result["b"], float)
        self.assertIsInstance(result["r"], float)
        self.assertIsInstance(result["t"], float)
        self.assertIsInstance(result["line"], Series)

    def test_log_geometric_mean(self):
        """Utility[Math]: Log Geometric Mean"""
        # returns = pandas_ta.percent_return(self.data.close)
        returns = percent_return(self.data.close)
        result = self.utils.log_geometric_mean(returns)
        self.assertIsInstance(result, float)

        result = self.utils.log_geometric_mean(Series([12, 14, 11, 8]))
        self.assertIsInstance(result, float)

        result = self.utils.log_geometric_mean(Series([100, 50, 0, 25, 0, 60]))
        self.assertIsInstance(result, float)

        series = Series([0, 1, 2, 3])
        result = self.utils.log_geometric_mean(series)
        self.assertIsInstance(result, float)

        result = self.utils.log_geometric_mean(-series)
        self.assertIsInstance(result, int)
        self.assertAlmostEqual(result, 0)

    def test_pascals_triangle(self):
        """Utility[Math]: Pascals Triangle"""
        self.assertIsNone(self.utils.pascals_triangle(inverse=True), None)

        array_1 = np.array([1])
        npt.assert_array_equal(self.utils.pascals_triangle(), array_1)
        npt.assert_array_equal(self.utils.pascals_triangle(weighted=True), array_1)
        npt.assert_array_equal(self.utils.pascals_triangle(weighted=True, inverse=True), np.array([0]))

        array_5 = self.utils.pascals_triangle(n=5)  # or np.array([1, 5, 10, 10, 5, 1])
        array_5w = array_5 / np.sum(array_5)
        array_5iw = 1 - array_5w
        npt.assert_array_equal(self.utils.pascals_triangle(n=-5), array_5)
        npt.assert_array_equal(self.utils.pascals_triangle(n=-5, weighted=True), array_5w)
        npt.assert_array_equal(self.utils.pascals_triangle(n=-5, weighted=True, inverse=True), array_5iw)

        npt.assert_array_equal(self.utils.pascals_triangle(n=5), array_5)
        npt.assert_array_equal(self.utils.pascals_triangle(n=5, weighted=True), array_5w)
        npt.assert_array_equal(self.utils.pascals_triangle(n=5, weighted=True, inverse=True), array_5iw)

    @skip
    def test__speed_test(self):
        """Utility[Core]: Indicator Speed Test"""
        result = self.utils.speed_test(self.data, top=10, talib=True, ascending=False, places=4)
        self.assertIsInstance(result, DataFrame)

        result = self.utils.speed_test(self.data, top=10, ascending=False, places=4)
        self.assertIsInstance(result, DataFrame)

    @skip
    def test__speed_test_excluded(self):
        """Utility[Core]: Indicator Speed Test sans Excluded"""
        # Top 3 Slowest with TA Lib since: 1/26/2022
        exclude = ["reflex", "td_seq", "trendflex"]
        exclude += ["ssf", "ssf3"]  # Top 5

        print(f"\n[i] excluded: {', '.join(exclude)}")
        result = self.utils.speed_test(self.data, excluded=exclude, top=5, talib=True, ascending=False, places=4, stats=False, verbose=True)
        self.assertIsInstance(result, DataFrame)

        # Top 3 Slowest without TA Lib since: 1/26/2022
        exclude = ["alligator", "qqe", "td_seq"]
        exclude += ["hilo", "psar"]  # Top 5

        print(f"\n[i] excluded: {', '.join(exclude)}")
        result = self.utils.speed_test(self.data, excluded=exclude, top=5, ascending=False, places=4, stats=False, verbose=True)
        self.assertIsInstance(result, DataFrame)

    # @skip
    def test__speed_test_verbose(self):
        """Utility[Core]: Verbose Indicator Speed Test"""
        # For precompiling njit functions
        result = self.utils.speed_test(self.data, top=5, talib=False, ascending=False, places=4, stats=False, verbose=False)

        result = self.utils.speed_test(self.data, top=5, talib=True, ascending=False, places=4, stats=False, verbose=True)
        self.assertIsInstance(result, DataFrame)

        result = self.utils.speed_test(self.data, top=5, ascending=False, places=4, stats=False, verbose=True)
        self.assertIsInstance(result, DataFrame)

    def test_symmetric_triangle(self):
        """Utility[Math]: Symmetric Triangle"""
        npt.assert_array_equal(self.utils.symmetric_triangle(), np.array([1,1]))
        npt.assert_array_equal(self.utils.symmetric_triangle(weighted=True), np.array([0.5, 0.5]))

        array_4 = self.utils.symmetric_triangle(n=4)  # or np.array([1, 2, 2, 1])
        array_4w = array_4 / np.sum(array_4)
        npt.assert_array_equal(self.utils.symmetric_triangle(n=4), array_4)
        npt.assert_array_equal(self.utils.symmetric_triangle(n=4, weighted=True), array_4w)

        array_5 = self.utils.symmetric_triangle(n=5)  # or np.array([1, 2, 3, 2, 1])
        array_5w = array_5 / np.sum(array_5)
        npt.assert_array_equal(self.utils.symmetric_triangle(n=5), array_5)
        npt.assert_array_equal(self.utils.symmetric_triangle(n=5, weighted=True), array_5w)

    def test_tal_ma(self):
        """Utility[TA]: TA Lib MA {str: int}"""
        self.assertEqual(self.utils.tal_ma("sma"), 0)
        self.assertEqual(self.utils.tal_ma("Sma"), 0)
        self.assertEqual(self.utils.tal_ma("ema"), 1)
        self.assertEqual(self.utils.tal_ma("wma"), 2)
        self.assertEqual(self.utils.tal_ma("dema"), 3)
        self.assertEqual(self.utils.tal_ma("tema"), 4)
        self.assertEqual(self.utils.tal_ma("trima"), 5)
        self.assertEqual(self.utils.tal_ma("kama"), 6)
        self.assertEqual(self.utils.tal_ma("mama"), 7)
        self.assertEqual(self.utils.tal_ma("t3"), 8)

    def test_zero(self):
        """Utility[Math]: Zero"""
        self.assertEqual(self.utils.zero(-0.0000000000000001), 0)
        self.assertEqual(self.utils.zero(0), 0)
        self.assertEqual(self.utils.zero(0.0), 0)
        self.assertEqual(self.utils.zero(0.0000000000000001), 0)

        self.assertNotEqual(self.utils.zero(-0.000000000000001), 0)
        self.assertNotEqual(self.utils.zero(0.000000000000001), 0)
        self.assertNotEqual(self.utils.zero(1), 0)

    def test_v_drift(self):
        """Validate: drift"""
        _instances = [0, None, "", [], {}, np.int8(5), np.int16(5), np.int32(5), np.int64(5)]
        for _ in _instances:
            self.assertIsInstance(self.utils.v_drift(_), int)

        self.assertEqual(self.utils.v_drift(-1.1), 1)
        self.assertEqual(self.utils.v_drift(0), 1)
        self.assertEqual(self.utils.v_drift(1.1), 1)
        self.assertEqual(self.utils.v_drift(5), 5)

        self.assertEqual(self.utils.v_drift(np.int64(-1.1)), -1) # np.int*() converts truncates floats
        self.assertEqual(self.utils.v_drift(np.int64(0)), 1)
        self.assertEqual(self.utils.v_drift(np.int64(1.1)), 1)
        self.assertEqual(self.utils.v_drift(np.int64(5)), 5)

    @skip
    def test_v_gtb(self):
        for s in [0, None, "", [], {}]:
            self.assertIsInstance(self.utils.v_gtb(s), (float, int))

        self.assertEqual(self.utils.v_drift(-1.1), 1)
        self.assertEqual(self.utils.v_drift(0), 1)
        self.assertEqual(self.utils.v_drift(1.1), 1)

    def test_v_lowerbound(self):
        """Validate: lowerbound"""
        _vars = [None, "", [], {}, -1.1, -1, 0.0, 0, 0.1, 1.0, 1]
        for strict in [True, False]:
            for v in _vars:
                self.assertIsInstance(self.utils.v_lowerbound(v, strict=strict), (float, int))

        self.assertEqual(self.utils.v_lowerbound(-1.1, 0), 0)
        self.assertEqual(self.utils.v_lowerbound(-1, 0), 0)
        self.assertEqual(self.utils.v_lowerbound(0.0, 0), 0)
        self.assertEqual(self.utils.v_lowerbound(0, 0), 0)
        self.assertEqual(self.utils.v_lowerbound(0.1, 0), 0.1)
        self.assertEqual(self.utils.v_lowerbound(1.0, 0), 1.0)
        self.assertEqual(self.utils.v_lowerbound(1, 0), 1)

        self.assertEqual(self.utils.v_lowerbound(-1.1, 0, strict=False), 0)
        self.assertEqual(self.utils.v_lowerbound(-1, 0, strict=False), 0)
        self.assertEqual(self.utils.v_lowerbound(0.0, 0, strict=False), 0.0)
        self.assertEqual(self.utils.v_lowerbound(0, 0, strict=False), 0)
        self.assertEqual(self.utils.v_lowerbound(0.1, 0, strict=False), 0.1)
        self.assertEqual(self.utils.v_lowerbound(1.0, 0, strict=False), 1)
        self.assertEqual(self.utils.v_lowerbound(1, 0, strict=False), 1)

    def test_v_upperbound(self):
        """Validate: upperbound"""
        _vars = [None, "", [], {}, -1.1, -1, 0.0, 0, 0.1, 1.0, 1]
        for strict in [True, False]:
            for v in _vars:
                self.assertIsInstance(self.utils.v_upperbound(v, strict=strict), (float, int))

    def test_v_offset(self):
        """Validate: offset"""
        _instances = [0, None, "", [], {}, np.int8(5), np.int16(5), np.int32(5), np.int64(5)]
        for _ in _instances:
            self.assertIsInstance(self.utils.v_offset(_), int)

        self.assertEqual(self.utils.v_offset(None), 0)
        self.assertEqual(self.utils.v_offset(-1.1), 0)
        self.assertEqual(self.utils.v_offset(-1), -1)
        self.assertEqual(self.utils.v_offset(0), 0)
        self.assertEqual(self.utils.v_offset(1.1), 0)
        self.assertEqual(self.utils.v_offset(1), 1)
        self.assertEqual(self.utils.v_offset(2), 2)

        self.assertEqual(self.utils.v_offset(np.int64(-1)), -1)
        self.assertEqual(self.utils.v_offset(np.int64(0)), 0)
        self.assertEqual(self.utils.v_offset(np.int64(1.1)), 1)
        self.assertEqual(self.utils.v_offset(np.int64(1)), 1)
        self.assertEqual(self.utils.v_offset(np.int64(2)), 2)
        self.assertEqual(self.utils.v_offset(np.int64(-1.1)), -1)
        self.assertEqual(self.utils.v_offset(np.int64(1.1)), 1)

    def test_sample_processes(self):
        """Feature[Math]: sample"""
        s0 = 0.01
        # tmp = pandas_ta.sample(length=2)
        tmp = pta_sample(length=2)
        processes, noises = tmp.processes, tmp.noises

        pn = [{"process": p, "noise": n} for p in processes for n in noises]
        for p in pn:
            # result = pandas_ta.sample(s0=s0, **p)
            result = pta_sample(s0=s0, **p)
            self.assertIsInstance(result.np, np.ndarray)
            self.assertEqual(result.np.size, 252)
            self.assertIsInstance(result.df, DataFrame)
            self.assertEqual(result.df.size, 252)

            nn = result.nonnegative(result.np)
            self.assertIsInstance(nn, np.ndarray)
            self.assertEqual(nn.size, 252)
            self.assertGreaterEqual(all(nn), 0)

            # result = pandas_ta.sample(s0=s0, length=20, **p)
            result = pta_sample(s0=s0, length=20, **p)
            self.assertIsInstance(result.np, np.ndarray)
            self.assertEqual(result.np.size, 20)
            self.assertIsInstance(result.df, DataFrame)
            self.assertEqual(result.df.size, 20)


    def test_to_utc(self):
        """Utility[Time]: to_utc"""
        result = self.utils.to_utc(self.data.copy())
        self.assertTrue(is_datetime64_ns_dtype(result.index))
        self.assertTrue(is_datetime64tz_dtype(result.index))

    @skip
    def test_total_time(self):
        """Utility[Time]: total_time"""
        result = self.utils.total_time(self.data)
        self.assertEqual(30.182539682539684, result)

        result = self.utils.total_time(self.data, "months")
        self.assertEqual(250.05753361606995, result)

        result = self.utils.total_time(self.data, "weeks")
        self.assertEqual(1086.5714285714287, result)

        result = self.utils.total_time(self.data, "days")
        self.assertEqual(7606, result)

        result = self.utils.total_time(self.data, "hours")
        self.assertEqual(182544, result)

        result = self.utils.total_time(self.data, "minutes")
        self.assertEqual(10952640.0, result)

        result = self.utils.total_time(self.data, "seconds")
        self.assertEqual(657158400.0, result)

    def test_version(self):
        """Utility[Core]: version"""
        result = pandas_ta.version
        self.assertIsInstance(result, str)
        print(f"\nPandas TA v{result}")
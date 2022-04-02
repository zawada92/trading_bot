from operator import itemgetter
from enum import Enum



class TrendDirection(Enum):
    UP, DOWN = range(1,3)
 
#TODO Potentialy its DoubleBottomTop class only.
# Another patterns will have their own classes.

class Pattern():

    def __init__(self, df) -> None:
        self.df = df

    def __get_avg_tops(self, avg) -> list:
        tops = []
        for i, v in enumerate(avg):
            if i < 1 or i > len(avg) - 2:
                continue
            if (v > avg[i-1] #and v > avg[i-2] and v > avg[i-3]
                and v > avg[i+1]):# and v > avg[i+2] and v > avg[i+3]):

                tops.append((i,v))

        return tops

    def _get_avg(self, opens, closes):
        avg = []
        for o, c in zip(opens, closes):
            avg.append((o+c)/2)
        
        return avg

    def _check_cdl_tops(self, top, sec_top, opens, closes):
        idx = top[0]
        sec_idx = sec_top[0]
        if idx < sec_idx:
            idx = idx - 1
            sec_idx = sec_idx + 1
        else:
            tmp = idx + 1
            idx = sec_idx - 1
            sec_idx = tmp
        
        max_open = max(opens[idx : sec_idx])
        max_close = max(closes[idx : sec_idx])
        max_body = max(max_open, max_close)
        trend_ranges = []
        prev_v = 0
        cur_range = dict.fromkeys(['start','stop','trend'])
        for i in range(idx, sec_idx):
            v = max(opens[i], closes[i])
            if prev_v == 0:
                cur_range['start'] = i
            elif v < prev_v:
                if cur_range['trend'] == None:
                    cur_range['trend'] = TrendDirection.DOWN
                elif cur_range['trend'] == TrendDirection.UP:
                    cur_range['stop'] = i - 1
                    trend_ranges.append(cur_range)
                    cur_range = dict.fromkeys(['start','stop','trend'])
                    cur_range['start'] = i - 1
                    cur_range['trend'] = TrendDirection.DOWN
            elif v > prev_v:
                if cur_range['trend'] == None:
                    cur_range['trend'] = TrendDirection.UP
                elif cur_range['trend'] == TrendDirection.DOWN:
                    cur_range['stop'] = i - 1
                    trend_ranges.append(cur_range)
                    cur_range = dict.fromkeys(['start','stop','trend'])
                    cur_range['start'] = i - 1
                    cur_range['trend'] = TrendDirection.UP

            prev_v = v
        cur_range['stop'] = sec_idx - 1
        trend_ranges.append(cur_range)

        print(trend_ranges)
        return trend_ranges

    def select_potential_tops(self, tops, opens, closes):

        for i, top in enumerate(tops):
            sec_top = 0
            if i + 1 < len(tops):
                sec_top = tops[i+1]
            if sec_top != 0:
                print(top, sec_top)
                self.check_cdl_tops(top, sec_top, opens, closes)
            
    def check_wicks(self, top_one_idx, top_two_idx):
        # TODO check also adjacent candle bodies
        df_len = len(self.df['low'])
        top1 = self.df.loc[[top_one_idx]]
        top2 = self.df.loc[[top_two_idx]]

        top1_dict = top1.to_dict(orient='records')
        top1_dict = top1_dict[0]
        top2_dict = top2.to_dict(orient='records')
        top2_dict = top2_dict[0]

        top1_body_top = max(top1_dict['open'], top1_dict['close'])
        top2_body_top = max(top2_dict['open'], top2_dict['close'])

        if (top1_dict['high'] < top2_dict["high"] and top1_dict["high"] > top2_body_top):
            return True
        if (top2_dict['high'] < top1_dict["high"] and top2_dict["high"] > top1_body_top):
            return True        

        return False

    def valid_tops(self, top_one_idx, top_two_idx):
        df_len = len(self.df['low'])
        top1 = self.df.loc[[top_one_idx]]
        top2 = self.df.loc[[top_two_idx]]
        top1_dict = top1.to_dict(orient='records')
        top1_dict = top1_dict[0]
        top2_dict = top2.to_dict(orient='records')
        top2_dict = top2_dict[0]
        self.df_sub_range = self.df['high'][top_one_idx + 1: top_two_idx - 1]
        top_sub_range = max(self.df_sub_range)
        if (top_sub_range > top1_dict['high'] or top_sub_range > top2_dict['high']):
            return False
        
        return True

    def check_ranges(self, trend_ranges):
        ranges_len = len(trend_ranges)
        for i in range(ranges_len):
            # check every combination of two tops for potential double top. Check if between them everything is smaller.
            if trend_ranges[i]['trend'] == TrendDirection.UP:
                top_idx = trend_ranges[i]['stop']
                j = 2
                while i + j < ranges_len:
                    next_top = trend_ranges[i + j]['stop']
                    if next_top - top_idx < 3:
                        print('continue for indx({},{})'.format(top_idx, next_top))
                        j = j + 2
                        continue
                    wicks_cross = self.check_wicks(top_idx, next_top)
                    if wicks_cross:
                        potential_tops = self.valid_tops(top_idx, next_top)
                        if potential_tops:
                            print("Double top idx:")
                            print((top_idx, next_top))
                            print((self.df['high'][top_idx], self.df['high'][next_top]))
                    j = j + 2
            
        return

    def is_double_top(self, msl_list):
        lows = self.df["low"]
        closes = self.df["close"]
        opens = self.df['open']
        avg = self.get_avg(opens, closes)
        avg_tops = self.get_avg_tops(avg)
        # avg_tops.sort(key=lambda tup: tup[1])
        avg_tops.sort(key=itemgetter(1))
        # print(avg_tops)
        # select_potential_tops(avg_tops, opens, closes)



        #my second approach 8.02.2022
        print('tomasz {}'.format(len(self.df["high"]) - 1))
        trend_ranges = self.check_cdl_tops((1, self.df["high"][1]), (len(self.df["high"]) - 1, self.df["high"][len(self.df["high"]) - 1]), self.df["low"], self.df["high"])
        """
        For each trend top (start of Down trend or end of up trend) starting from most left one:
            got for next top:
                check if it can form double top
                if no then check if its highier than left top:
                    if yest then finish this top next checking
                    if no then go for next top
                
        checking if two can form double top:
            check one left this one an one right wick up. Pick bigest high. Make a range from bigest high to the body of candle.
            Above do for both.
            Check if ranges are crossing. If yes then it can be potential double top.
                Check if between them there are higs which are also crossing some of their ranges.
                If there are not then ok it can be double top.
                if there are some then check if this highs are higher than some of the two ranges -> its not a double top then.
                Check the pullback. How low where we between thes two tops. Range between lowest low and lowest body.
                Then we have our neckline.
                Check if next candles direct down to neckline.
                
        """
        self.check_ranges(trend_ranges)
        
        
        
        
        
        
        
        
        # todo check trend and latest 3 MSL
        # create structure of ranges from MSLs (ranges of MSLs)
        # find min and max in MSLs. Then set a percent of this difference which can be set as range in which MSLs are one MSL.

        # last_msl = msl_list[-1]
        # min_low = min(lows)
        # min_close = min(closes)

        # lookup_range = {"min": min_low, "max": min_close}

        # in_range_counter = 0
        # above_range_counter = 0
        # for low, close in lows, closes:
        #     if low < lookup_range["max"]:
        #         in_range_counter += 1
        #     if close > lookup_range["max"]:
        #         above_range_counter += 1

        # print(in_range_counter)
        # print(above_range_counter)


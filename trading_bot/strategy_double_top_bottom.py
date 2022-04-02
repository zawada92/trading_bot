# def morning_star_20_ema():
#     api = ExchangeApi()
#     # api.poll_data (contract="BTC_USDT", limit=1000, interval="15m", delay="1m")
#     data = api.get_candle_stick(contract="BTC_USDT", limit=62, interval="1h")
#     indicator = Indicators()
#     data_df = indicator.init_data_frame(data)
#     indicator.add_ema(data_df, 20)
#     fib_382 = indicator.fib_382_cdl(data_df)
#     indicator.add_atr(data_df)

#     PlotData.my_plot(data_df, [], fib_382)
#     df_tail = data_df[-61:-1]
#     df_tail.reset_index(drop=True, inplace=True)
#     patterns = Pattern(df_tail)
#     patterns.is_double_top([])
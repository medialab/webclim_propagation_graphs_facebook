    # We prepare a dataframe to import the facebook group nodes with specific attributes:
    # - the number of followers -> node size
    # - the ratio of health fake news being shared vs. climate fake news -> node color
    #   (green = a group sharing only fake news about health, blue = only about climate)
    fb_group_df = posts_df.groupby('account_id')['field'].apply(list)\
        .to_frame().reset_index()
    fb_group_df["health_ratio"] = (fb_group_df["field"].apply(lambda x: x.count('health')) /
                                   fb_group_df["field"].apply(len))
    fb_group_df = fb_group_df.merge(posts_df[['account_id', 'account_name', 'account_subscriber_count']]\
                             .sort_values(by="account_subscriber_count", ascending=True)\
                             .drop_duplicates(subset = ['account_id'], keep='last'),
                             left_on='account_id', right_on='account_id', how='left')


def color_gradient(ratio):
    """Return an HEX color between green and blue, depeding on the ratio value
    (0 = blue, 1 = yellow)"""
    blue_color = np.array(mpl.colors.to_rgb('#1f77b4'))
    yellow_color = np.array(mpl.colors.to_rgb('#ffea00'))
    return mpl.colors.to_hex((1 - ratio) * blue_color + ratio * yellow_color)
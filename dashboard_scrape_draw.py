from network_graph import DrawNetworkGraph
from subreddit_relations import SubredditRelations
import pandas as pd


if __name__ == '__main__':
    from network_graph import DrawNetworkGraph
    from subreddit_relations import SubredditRelations
    import pandas as pd
    relations = SubredditRelations()
    subreddit_list = relations.top_100_subreddits(1)
    relations_dict = relations.find_relations(subreddit_list)
    relations_df = pd.DataFrame(relations_dict).fillna(0)
    print(relations.comment_upvote)
    network_graph = DrawNetworkGraph()
    network_graph.dashboard_graph(relations_df)

import sys
import pandas as pd
import numpy as np
import argparse
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
import os
import tqdm
sns.set_style('darkgrid')
sns.set_palette('Set2')

def config(parser):
    parser.add_argument('--input_file')
    parser.add_argument('--corpus')
    parser.add_argument('--output_path')
    parser.add_argument('--iterations', type=int, default=1)
    return parser

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser = config(parser)
    args = parser.parse_args()
    output_path = os.path.join('./', args.output_path)
    if not os.path.exists(output_path):
       os.makedirs(output_path)

    threshold_label = ['belief_label', 'truth_label', 'understanding_label']
    if args.corpus == 'NYT':
        time_scale = 'year'
        extra_field = 'section_grp'
        x_label = 'Year'
        roll_interval = 3
    elif args.corpus == 'Twitter':
        time_scale = 'year_month'
        extra_field = 'party'
        x_label = 'Year'
        roll_interval = 3

    if args.corpus == 'Twitter':
        full_df = pd.read_csv(args.input_file, usecols=['id','created_at','party']+threshold_label)
    elif args.corpus == 'NYT':
        full_df = pd.read_csv(args.input_file, usecols=['id','created_at','section']+threshold_label)
        grp_dict = {"U.S.":"UWW", "World":"UWW", "Washington":"UWW", "Health":"HSEC", "Science":"HSEC", 
                    "Education":"HSEC", "Climate":"HSEC", "Opinion":"OP"}
        full_df['section_grp'] = full_df.section.apply(lambda x: grp_dict[x])
        #print(full_df['section_grp'].value_counts())

    def get_sample_df(full_df):
        full_df = full_df.sample(frac=1.0, replace=True)
        df_dict = {}
        for tl in threshold_label:
            df_dict[tl] = full_df[full_df[tl] > 0]
            df_dict[tl] = df_dict[tl].drop_duplicates(subset='id')

        if args.corpus == 'NYT':
            for tl in threshold_label:
                df_dict[tl]['created_at'] = pd.to_datetime(df_dict[tl]['created_at'])
                df_dict[tl][time_scale] = df_dict[tl]['created_at'].dt.year 
            full_df['created_at'] = pd.to_datetime(full_df['created_at'])
            full_df[time_scale] = full_df['created_at'].dt.year
        elif args.corpus == 'Twitter':
            for tl in threshold_label:
                df_dict[tl]['created_at'] = pd.to_datetime(df_dict[tl]['created_at'])
                df_dict[tl][time_scale] = pd.to_datetime(df_dict[tl]['created_at'].dt.strftime('%Y-%m'))
            full_df['created_at'] = pd.to_datetime(full_df['created_at'])
            full_df[time_scale] = pd.to_datetime(full_df['created_at'].dt.strftime('%Y-%m'))
        else:
            sys.exit('corpus not supported')

        for tl in threshold_label:
            df_dict[tl] = df_dict[tl].sort_values(by=time_scale)
            #df_dict[tl] = df_dict[tl].dropna()
        full_df_time = full_df[['id',time_scale,extra_field]]
        full_df_time = full_df_time.drop_duplicates(subset='id')
        #full_df_time = full_df_time.dropna()
        full_df_time = full_df_time.sort_values(by=time_scale) 
        return df_dict, full_df_time

    sample_dict = {}
    sample_full = pd.DataFrame()
    for _ in tqdm.trange(args.iterations):
        df_dict, full_df_time = get_sample_df(full_df)
        agg_full = full_df_time.groupby([time_scale, extra_field])['id'].agg(['count'])#.reset_index()
        for i, tl in enumerate(threshold_label):
            agg_cat = df_dict[tl].groupby([time_scale, extra_field])['id'].agg(['count'])#.unstack().stack(dropna=False)#.reset_index()
        #print(agg_cat.head())
        #print(agg_full.head())
            if len(agg_cat) != len(agg_full):
                print(" Time scale of full corpus doesn't match subcorpus")
                print(len(agg_cat), len(agg_full))
                #print(agg_cat.head())
            agg_cat = agg_cat.join(agg_full, how='left', rsuffix='_full')
            agg_cat = agg_cat.reset_index()
            agg_cat['count_rel'] = agg_cat['count'] / agg_cat['count_full']
            #print(agg_cat.head())
            agg_rolling = agg_cat.groupby(extra_field)['count_rel'].rolling(roll_interval).mean().reset_index()
            agg_cat.index.names = ['level_1']
            agg_cat.reset_index(inplace=True)
            #print(len(agg_cat), len(agg_rolling))
            #print(agg_cat.columns, agg_rolling.columns)
            agg_cat = agg_cat.join(agg_rolling.set_index(['level_1', extra_field]), on=['level_1', extra_field], how='left', rsuffix='_ma') 
            if tl in sample_dict.keys():
                sample_dict[tl] = pd.concat([sample_dict[tl], agg_cat])
            else:
                sample_dict[tl] = agg_cat
        sample_full = pd.concat([sample_full, agg_full.reset_index()])

    alpha = 5
    l95 = lambda x: np.nanpercentile(x, alpha/2)
    u95 = lambda x: np.nanpercentile(x, 100-alpha/2)
    def sample_aggregate(x, column):
        result = {}
        result['mean'] = np.nanmean(x[column])
        result['l95'] = np.nanpercentile(x[column], alpha/2)
        result['u95'] = np.nanpercentile(x[column], 100-alpha/2)
        return pd.Series(result, index=['mean', 'l95', 'u95'])

    plt.figure(figsize=(12, 18))
    nrows = len(threshold_label) + 1
    fig, axes = plt.subplots(nrows,1, sharex=True)

    sample_full_agg = sample_full.groupby([time_scale, extra_field]).apply(sample_aggregate, column='count').reset_index()
    sample_full_agg.to_csv('sample_full_agg.csv', index=False)
    for i, tl in enumerate(threshold_label):
        sample_agg = sample_dict[tl].groupby([time_scale, extra_field]).apply(sample_aggregate, column='count_rel_ma').reset_index()
        sample_agg.to_csv(f'sample_agg_{tl}.csv', index=False)
        label = tl.split('_')[0]
        axes[i].set_title(label)
        if args.corpus == 'Twitter':
            palette = {"Democrat": "blue", "Republican": "red"}
            colors = {"Democrat": "tab:blue", "Republican": "tab:red"}
            axes[i].axvline(x=pd.to_datetime('2016-11-01'), color='black', linestyle='--')
            axes[i].axvline(x=pd.to_datetime('2020-11-01'), color='black', linestyle='--')
        elif args.corpus == 'NYT':
            palette = {"HSEC": "green", "OP": "red", "UWW": "blue"}
            colors = {"HSEC": "tab:green", "OP": "tab:red", "UWW": "tab:blue"}

        for grp_name, grp in sample_agg.groupby(extra_field):
            axes[i].plot(time_scale, 'mean', data=grp,  color=colors[grp_name], label=grp_name, linewidth=1)
            axes[i].fill_between(x=time_scale, y1='l95', y2='u95', data=grp,  alpha=0.4, color=colors[grp_name])
            axes[i].set_ylabel('.', color=(0, 0, 0, 0))

    lines = [] 
    for grp_name, grp in sample_full_agg.groupby(extra_field):
        line, = axes[-1].plot(time_scale, 'mean', data=grp,  color=colors[grp_name], label=grp_name, linewidth=1)
        lines.append(line)
        axes[-1].fill_between(x=time_scale, y1='l95', y2='u95', data=grp,  alpha=0.4, color=colors[grp_name])

    if args.corpus == 'Twitter':
        axes[-1].axvline(x=pd.to_datetime('2016-11-01'), color='black', linestyle='--')
        axes[-1].axvline(x=pd.to_datetime('2020-11-01'), color='black', linestyle='--')
    
    ymax = max([ax.get_ylim()[1] for ax in axes[:-1]])
    axes[0].set_ybound(upper=ymax)
    for i, _ in enumerate(axes[:-1]):
        if i > 0:
            axes[i].sharey(axes[i-1]) 
           #axes[i].set_ybound(upper=ymax)
    #line, label = ax.get_legend_handles_labels()
    fig.legend(handles=lines, loc='upper right') 
    fig.text(0.04, 0.5, 'Rel. Frequency', va='center', ha='center', rotation='vertical')
    plt.xlabel(x_label)
    plt.ylabel('Frequency')
    plt.suptitle(args.corpus)
    plt.tight_layout()
    
    #f.supylabel('Frequency')
    #plt.legend(loc=1, bbox_to_anchor=(1,1))
    fn_plot = os.path.join(output_path, 'frequency_plot.svg')
    plt.savefig(fn_plot, format='svg', dpi=300) 
    plt.close()

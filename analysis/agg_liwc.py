import sys
import pandas as pd
import numpy as np
import argparse
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
import os
import tqdm

sns.set_style('white')
#sns.set_palette('Set2')
plt.rc("axes.spines", top=False, right=False)

def config(parser):
    parser.add_argument('--input_file')
    parser.add_argument('--corpus')
    parser.add_argument('--full_liwc')
    #parser.add_argument('--full_id_date')
    parser.add_argument('--output_path')
    parser.add_argument('--use_threshold_label', default=False, action='store_true')
    parser.add_argument('--remove_hsec', default=False, action='store_true')
    parser.add_argument('--iterations', type=int, default=1)
    return parser

def bootstrap_df(df):
    result = pd.DataFrame()
    for _ in range(10000):
        sample_df = df.groupby([time_scale, extra_field]).sample(frac=1.0, replace=True)#compute the metric here
        result.append(sample_df)
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser = config(parser)
    args = parser.parse_args()
    output_path = os.path.join('./', args.output_path)
    if not os.path.exists(output_path):
       os.makedirs(output_path)

    cols = ['emo_neg', 'emo_pos','Authentic','Analytic','moral']#'emotion', 
    threshold_label = ['belief_label', 'truth_label']#, 'understanding_label'

    if args.corpus == 'Twitter':
        label_fld = threshold_label + ['party'] if args.use_threshold_label else ['max_label']
        liwc_df = pd.read_csv(args.input_file, usecols=['id','created_at']+label_fld)
        liwc_df['id'] = liwc_df.id.apply(lambda x: x.strip('"'))
        liwc_df = liwc_df[liwc_df.party.isin(['Republican', 'Democrat'])]
    elif args.corpus == 'NYT':
        label_fld = threshold_label + ['section'] if args.use_threshold_label else ['max_label']
        grp_dict = {"U.S.":"UWW", "World":"UWW", "Washington":"UWW", "Health":"HSEC", "Science":"HSEC", 
                    "Education":"HSEC", "Climate":"HSEC", "Opinion":"OP"}
        liwc_df = pd.read_csv(args.input_file, usecols=['id','created_at']+label_fld)
        liwc_df['id'] = liwc_df.id.apply(lambda x: x.strip('"'))
        liwc_df['section_grp'] = liwc_df.section.apply(lambda x: grp_dict[x])
        if args.remove_hsec:
           liwc_df = liwc_df[liwc_df['section_grp'] != 'HSEC']

    #if args.corpus == 'Twitter':
    #    liwc_df['id'] = liwc_df['id'].astype(int)


    print(len(pd.to_datetime(liwc_df['created_at']).dt.year.unique()))
    #full_id_date = pd.read_csv(args.full_id_date, usecols=['id','created_at'])
    #if args.corpus == 'Twitter':
    #    full_id_date['id'] = full_id_date['id'].astype(int)
    #print(len(pd.to_datetime(full_id_date['created_at']).dt.year.unique()))
    full_liwc_df = pd.read_csv(args.full_liwc,usecols=['id','WC']+cols)
    full_liwc_df['id'] = full_liwc_df.id.apply(lambda x: x.strip('"'))
    #if args.corpus == 'Twitter':
    #    full_liwc_df['id'] = full_liwc_df['id'].astype(int)
    print(f'Initial length: subset is {len(liwc_df)}, full is {len(full_liwc_df)}')
    full_liwc = liwc_df.join(full_liwc_df.set_index('id'), on='id', how='left')
    full_liwc = full_liwc.dropna()

    df_dict = {}
    if args.use_threshold_label:
        for tl in threshold_label:
            #df_dict[tl] = df_dict[tl].join(full_liwc.set_index(['id']), on=['id'], how='left', rsuffix='DROP').filter(regex="^(?!.*DROP)")
            df_dict[tl] = full_liwc[full_liwc[tl] > 0]
            df_dict[tl] = df_dict[tl].drop_duplicates(subset='id')
    else:
        #liwc = liwc_df.join(full_liwc.set_index(['id']), on=['id'], how='left', rsuffix='DROP').filter(regex="^(?!.*DROP)")
        liwc = full_liwc[full_liwc['max_label'] != 'unknown']
        print(len(pd.to_datetime(liwc['created_at']).dt.year.unique()))
        print(len(pd.to_datetime(full_liwc['created_at']).dt.year.unique()))
        liwc = liwc.drop_duplicates(subset='id')
        #print(len(pd.to_datetime(liwc['created_at']).dt.year.unique()))
    full_liwc = full_liwc.drop_duplicates(subset='id')
    #print(len(pd.to_datetime(full_liwc['created_at']).dt.year.unique()))
        #    print(f'After join: subset is {len(liwc)}, full is {len(full_liwc)}')

    if args.corpus == 'NYT':
        time_scale = 'year'
        x_label = 'Year'
        roll_interval = 3
        extra_field = 'section_grp'
        if args.use_threshold_label:
            for tl in threshold_label:
                df_dict[tl]['created_at'] = pd.to_datetime(df_dict[tl]['created_at'])
                df_dict[tl][time_scale] = df_dict[tl]['created_at'].dt.year 
        else:
            liwc['created_at'] = pd.to_datetime(liwc['created_at'])
            liwc[time_scale] = liwc['created_at'].dt.year

        full_liwc['created_at'] = pd.to_datetime(full_liwc['created_at'])
        full_liwc[time_scale] = full_liwc['created_at'].dt.year
        #liwc = liwc[liwc[time_scale] > 1980]
        #full_liwc = full_liwc[full_liwc[time_scale] > 1980]
        #print(full_liwc[time_scale].unique())
        #liwc.to_csv('/data/honesty/corpora/NYT/NYT-API/NYT_id_label_liwc.csv', index=False)
        #sys.exit()
    elif args.corpus == 'Twitter':
        time_scale = 'year_month'
        x_label = 'Year'
        roll_interval = 3
        extra_field = 'party'
        if args.use_threshold_label:
            for tl in threshold_label:
                df_dict[tl]['created_at'] = pd.to_datetime(df_dict[tl]['created_at'])
                df_dict[tl][time_scale] = pd.to_datetime(df_dict[tl]['created_at'].dt.strftime('%Y-%m'))
                df_dict[tl]['year'] = df_dict[tl]['created_at'].dt.year
                df_dict[tl] = df_dict[tl][df_dict[tl]['year'] > 2014]
        else:
            liwc['created_at'] = pd.to_datetime(liwc['created_at'])
            liwc[time_scale] = pd.to_datetime(liwc['created_at'].dt.strftime('%Y-%m'))
        full_liwc['created_at'] = pd.to_datetime(full_liwc['created_at'])
        full_liwc[time_scale] = pd.to_datetime(full_liwc['created_at'].dt.strftime('%Y-%m'))
        full_liwc['year'] = full_liwc['created_at'].dt.year
        full_liwc = full_liwc[full_liwc['year'] > 2014]
        #print(full_liwc[time_scale].unique())
    else:
        sys.exit('corpus not supported')
    
    wtd_avg_full = lambda x: np.ma.average(np.ma.MaskedArray(x, mask=np.isnan(x))/100, weights=full_liwc.loc[x.index, "WC"])
    wtd_avg = lambda x: np.average(x/100, weights=liwc.loc[x.index, "WC"] )
    if args.use_threshold_label:
        for tl in threshold_label:
            df_dict[tl] = df_dict[tl].sort_values(by=time_scale)
            #df_dict[tl] = df_dict[tl].dropna()
    else:
        liwc = liwc.sort_values(by=time_scale) 
        liwc = liwc.dropna()

    full_liwc = full_liwc.sort_values(by=time_scale) 
    #full_liwc = full_liwc.dropna()
    #####
    if args.use_threshold_label:
        for col in tqdm.tqdm(cols):
            plt.figure(figsize=(12, 18))
            nrows = len(threshold_label) + 1
            fig, axes = plt.subplots(nrows,1, sharex=True)
            for i, tl in enumerate(threshold_label):
                wtd_avg = lambda x: np.average(x/100, weights=df_dict[tl].loc[x.index, "WC"])
                agg_full = full_liwc.groupby([time_scale, extra_field]).agg({col:wtd_avg_full})#.unstack().stack(dropna=False)
                #print(agg_cat.columns)
                sample_df = pd.DataFrame()
                for _ in tqdm.trange(args.iterations):
                    agg_cat = df_dict[tl].groupby([time_scale, extra_field]).sample(frac=1.0, replace=True)#.agg({col:wtd_avg})#.unstack().stack(dropna=False)
                    agg_cat = agg_cat.groupby([time_scale, extra_field]).agg({col:wtd_avg})
                    #print(agg_full.columns)
                    if len(agg_cat) != len(agg_full):
                        print(" Time scale of full corpus doesn't match subcorpus")
                        print(len(agg_cat), len(agg_full))
                        print(agg_cat.head())
                    agg_cat = agg_cat.join(agg_full, how='left', rsuffix='_full')
                    agg_cat = agg_cat.reset_index()
                    agg_cat[f'{col}_rel'] = agg_cat[col] / agg_cat[f'{col}_full']
                    #print(agg_cat.head())
                    
                    agg_rolling = agg_cat.groupby(extra_field)[f'{col}_rel'].rolling(roll_interval).mean().reset_index()#, min_periods=1
                    agg_cat.index.names = ['level_1']
                    agg_cat.reset_index(inplace=True)
                    #print(len(agg_cat), len(agg_rolling))
                    #print(agg_cat.columns, agg_rolling.columns)
                    agg_cat = agg_cat.join(agg_rolling.set_index(['level_1', extra_field]), on=['level_1', extra_field], how='left', rsuffix='_ma') 
                    #print(agg_cat.sort_values(by=[time_scale,extra_field]).tail(25))
                    sample_df = pd.concat([sample_df, agg_cat[[time_scale, extra_field, f'{col}_rel_ma']]])

                alpha = 5
                l95 = lambda x: np.nanpercentile(x, alpha/2)
                u95 = lambda x: np.nanpercentile(x, 100-alpha/2)
                def sample_aggregate(x):
                    result = {}
                    result['mean'] = np.nanmean(x[f'{col}_rel_ma'])
                    result['l95'] = np.nanpercentile(x[f'{col}_rel_ma'], alpha/2)
                    result['u95'] = np.nanpercentile(x[f'{col}_rel_ma'], 100-alpha/2)
                    return pd.Series(result, index=['mean', 'l95', 'u95'])

                sample_agg = sample_df.groupby([time_scale, extra_field]).apply(sample_aggregate).reset_index()
                #print(sample_agg.head()) 
                agg_full = agg_full.reset_index()

                sample_agg.to_csv(f'sample_agg_{col}_{tl}.csv', index=False)
                agg_full.to_csv(f'agg_full_{col}_{tl}.csv', index=False)                

                label = tl.split('_')[0]
                axes[i].set_title(label)
                if args.corpus == 'Twitter':
                    palette = {"Democrat": "blue", "Republican": "red"}
                    #colors = {"Democrat": "tab:blue", "Republican": "tab:red"}
                    colors = {"Democrat": "#0015BC", "Republican": "#FF0000"}
                    axes[i].axvline(x=pd.to_datetime('2016-11-01'), color='black', linestyle='--')
                    axes[i].axvline(x=pd.to_datetime('2020-11-01'), color='black', linestyle='--')
                elif args.corpus == 'NYT':
                    palette = {"HSEC": "green", "OP": "red", "UWW": "blue"}
                    colors = {"HSEC": "tab:green", "OP": "tab:red", "UWW": "tab:blue"}
                #ax = sns.lineplot(x=sample_agg[time_scale], y=sample_agg['mean'], marker='o', ax=axes[i], hue=extra_field, data=sample_agg, palette=palette)
                for grp_name, grp in sample_agg.groupby(extra_field):
                    axes[i].plot(grp[time_scale], grp['mean'], color=colors[grp_name], label=grp_name, linewidth=1)
                    axes[i].fill_between(x=time_scale, y1='l95', y2='u95', data=grp,  alpha=0.4, color=colors[grp_name])
                    #axes[i].get_legend().remove()
                    axes[i].set_ylabel('.', color=(0, 0, 0, 0))
                axes[i].axhline(y=1.0, color="black", linestyle="--")
            lines = [] 
            for grp_name, grp in agg_full.groupby(extra_field):
                line,  = axes[-1].plot(grp[time_scale], grp[col], color=colors[grp_name], label=grp_name, linewidth=1)
                lines.append(line)
                #ax1 = sns.lineplot(x=agg_full[time_scale], y=agg_full[col], marker='.',ax=axes[-1], hue=extra_field, data=agg_full, palette=palette)
            if args.corpus == 'Twitter':
                axes[-1].axvline(x=pd.to_datetime('2016-11-01'), color='black', linestyle='--')
                axes[-1].axvline(x=pd.to_datetime('2020-11-01'), color='black', linestyle='--')
            #ax1.set_ylabel(f'{col} score')
            #ax1.get_legend().remove()
            fig.text(0.04, 0.5, f'Rel. {col} score', va='center', ha='center', rotation='vertical')
            ymax = max([ax.get_ylim()[1] for ax in axes[:-1]])
            axes[0].set_ybound(upper=ymax)
            for i, _ in enumerate(axes[:-1]):
                if i > 0:
                    axes[i].sharey(axes[i-1]) 
                    #axes[i].set_ybound(upper=ymax)
            plt.xlabel(x_label)
            plt.ylabel(f'{col} score')
            plt.suptitle(args.corpus)
            #plt.legend(loc=1, bbox_to_anchor=(1,1))
            #line, label = axes[0].get_legend_handles_labels()
            fig.legend(handles=lines, loc='upper right') 
            fn_plot = os.path.join(output_path, f'{col}_plot.svg')
            plt.tight_layout()
            plt.savefig(fn_plot, format='svg', dpi=300) 
            #plt.savefig(fn_plot, format='png', dpi=300) 
            plt.close()
    else:
        for col in cols:
            agg_liwc = liwc.groupby(['max_label',time_scale]).agg({col:wtd_avg}).reset_index()
            agg_full = full_liwc.groupby([time_scale]).agg({col:wtd_avg_full}).reset_index()
            agg_full_concat = pd.concat([agg_full]*3, ignore_index=True)
            if len(agg_liwc) == len(agg_full_concat) :
                agg_liwc[col] = agg_liwc[col]/agg_full_concat[col]
            else:
                print(" Time scale of full corpus doesn't match subcorpus")

            print("\n----------- Minimum -----------\n")
            print(f'{col} min is {agg_liwc[col].min()}')
            print("\n----------- Maximum -----------\n") 
            print(f'{col} max is {agg_liwc[col].max()}')
            fn_liwc = os.path.join(output_path, f'{args.corpus}_liwc_{col}_agg.csv')
            agg_liwc.to_csv(fn_liwc, index=False)
            fn_full = os.path.join(output_path, f'{args.corpus}_full_liwc_{col}_agg.csv')
            agg_full.to_csv(fn_full, index=False)
                #pivot into wide form
            pivot = agg_liwc.pivot(index=time_scale, columns='max_label', values=col).reset_index()
            plt.figure(figsize=(12, 9))
            plt.title(args.corpus)
            plt.ylabel(f'{col} score')
            f, axes = plt.subplots(2,1, sharex=True)
            axes[0].set_title(args.corpus)
            for cat in ['belief','truth','understanding']:
                #pivot[col] = (pivot[col] - pivot[col].min())/(pivot[col].max() - pivot[col].min())
                #line plot of each label 
                pivot[cat] = pivot[cat].rolling(roll_interval).mean()
                print(pivot.head())
                ax = sns.lineplot(x=pivot[time_scale], y=pivot[cat],label=cat, marker='o',ax=axes[0])
                ax.set_ylabel(f'{col} score')
            ax1 = sns.lineplot(x=agg_full[time_scale], y=agg_full[col],label=col, marker='o',ax=axes[1])
            ax1.set_ylabel(f'{col} score')
            plt.xlabel(x_label)
            #plt.legend(loc=1, bbox_to_anchor=(1,1))
            fn_plot = os.path.join(output_path, f'{col}_plot.png')
            plt.savefig(fn_plot) 
            plt.close()
        
        

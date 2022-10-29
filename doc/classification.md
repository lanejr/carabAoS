# Army List Classification

This document will briefly touch on the motivation, then discuss the thought process behind the techniques used by the army classifier tool. It will also give some guidance on hyperparameter tuning and knowledge bank curation, which are both fundamental to the classifier's effectiveness.

## Motivation

Army list archetypes are not a novel concept, many players will have heard nicknames like 'Morathi and bow snakes', 'Nurgle flies', and even whimsical ones like 'oops all Magmadroths'. Immediately upon hearing one of these archetypes a competitive player will have a strong idea of what most of the army list being referred to looks like. They are a very useful communicative tool for quickly describing an army and how it plays.

One of the most fun things about factions having strong internal balance is that multiple types of armies can be competitively viable from within the same faction. Additionally, as the metagame shifts through seasonal rules changes, points updates and new releases, these army archetypes will rise and fall in effectiveness and popularity. Looking solely at statistics by faction overlooks this whole aspect of the metagame.

Consider a scenario where a dominant faction has a stronger army type and a weaker army type. Suppose that units in the stronger army type are nerfed such that it loses dominance. Then the metagame shifts as armies that had success by effectively countering it also fade, and now the previously weaker army type becomes dominant, albeit to a lesser extent, in their absence. If faction winrates alone were observed it may seem like the nerfs were ineffective, but in reality they changed the whole metagame.

Being able to effectively classify army lists at a finer granularity than the faction level, but still in broad enough categories that meaningful amounts of data could be collected for each, allows for a much more accurate and interesting view of the metagame over time. This is the problem the classifier tool attempts to solve by providing an intuitive yet automated solution for classifying army lists into established archetypes.

## Feature Selection

A core assumption being made by the classifier is that army lists contain lots of noise - data that is irrelevant for their classification. It is certainly possible to define archetypes using every aspect of an army list, from faction and subfaction down to wargear choices on battleline units (in fact I did this in my prototype for this project), but in reality some pieces of information are very important and some are not important at all.

In machine learning a key technique is dimensionality reduction. Left unchecked, an algorithm will scrutinise every piece of information provided and focus on the wrong things - a competitive player would not look at two armies with the same faction, subfaction, grand strategy, and battalions but completely different units and think they are the same archetype, but a computer might. One way to tackle this problem is to attach 'weights' to each feature defining its importance, but often it is even more effective (for a variety of reasons) to simply drop features that are less relevant - not to mention the fact that tuning each of these weights correctly is its own challenge.

Being ruthless with our data, we flatten an army list down to just its faction, warscrolls and enhancements that define the core essence of the army. This choice is reinforced by the first Warhammer community [AoS metawatch](https://www.warhammer-community.com/2022/09/29/metawatch-how-the-warhammer-age-of-sigmar-team-uses-tournament-data-to-balance-the-game/) article, which notes the design team's focus on warscroll and enhancement inclusion rates. Within the algorithm the classifier uses, the importance of warscroll and enhancement similarity between two army lists can be optionally weighted as discussed above, giving the user more control over the relative importance of these remaining features (discussed further [below](#hyperparameter-tuning)).

## Algorithm Choices

The reasoning behind choosing the k-nearest neighbours algorithm for this classifier tool was relatively simple: it has no separate training phase before it can classify data, and its internals are all observable and even manipulable. This section will explain more about why each of these aspects is desirable, and contrast against other popular classification approaches, then discuss in more detail the approach taken.

### Lazy Learning

Machine learning algorithms can be divided into two categories: eager learning and lazy learning. In the context of classification, those that perform eager learning first undergo a training phase where they are fed training data and build a classification model, then once the training is complete this general model can be applied to classify any new piece of data. The main advantage is that the trained model is usually very quick to work, and very small compared to the amount of data used to create it. With the modern abundance of data this has become a really popular approach for many applicationss, where an enormous number of data points can be used to hone an extremely effective model that is a fraction of the size - artificial neural networks or decision trees are good examples.

Lazy learning algorithms on the other hand have no training step, they use their entire data set every time they classify a new piece of data, and so comparatively take up a lot more space, and tend to be slower as well. What this means, however, is that every new piece of data the algorithm classifies can be added into its 'training data' set and immediately learned from to help classify the next data piece. This allows lazy learning approaches to very quickly adapt to changes in data that would render an eager learning model obselete.

For classifying army lists in a shifting meta, having to constantly train and update an eager learning model would be inconvenient, where effective lazy learning solutions exist that are far more adaptable. Also, our data set is never likely to be too large, so the downsides of lazy learning would have no material effect on performance.

### Observability

Some machine learning approaches operate like a 'black box', where the user has no knowledge of the algorithm's decision making process. In many cases this is not an issue, but it does require a certain amount of trust in the model. For this classifier tool, the user should not have to trust the model, so full visibility of its decision making process is ideal.

Taking this a step further, some approaches have good observability, but in practice may still be difficult to reason about. For example, a decision tree clearly defines how it makes decisions: at each step it asks a question of the data, then moves to the next step (like a flow chart) until it makes a decision. A common extension of a decision tree is a random forest, where many smaller decision trees (trained on separate small data sets) all simultaneously make a decision and the most common response is chosen. These are still technically observable, but an observer will have to spend a long time reading through many decision trees to reason about a single decision.

This is not ideal, for this classifier an observer should be able to intuitively reason about what decision will be made based on the data available. If the data set is too large the observer may face a similar challenge, however the expectation is that the data set is carefully pruned over time, or even curated.

### k-Nearest Neighbours

A popular algorithm that fits our lazy learning and observability criteria is k-nearest neighbours. The approach is very simple: we start with some labelled 'training data', then when we want to classify a new piece of data we see how 'close' it is to each of our pieces of training data, then choose the most popular label from the closest 'k', where 'k' is a number we choose.

To visualise how this works, imagine we have in our training data the numbers `1`, and `2` labelled `A`, and the numbers `11`, `13`, `15` labelled `B`, and we choose 'k' to be 3. If we now want to label the number `4`, we need to find the 'k' closest training data points, which would be `1`, `2` and `11`. Then we look for the most common label amongst our 'k', having labels `A`, `A`, and `B` respectively, which would be `A`. Therefore we label `4` as `A`, and we can even add it to our training data set as well to help classify more data.

Hopefully this simple example shows how intuitive the approach is, and how a user can generally reason about the decision making process in their head by looking at the training data set.

### Levenshtein Distance

The challenge when applying this algorithm to more complex data such as army lists is finding an appropriate way to measure how 'close' two data points are. We have already flattened our army list down to just its faction, warscrolls and enhancements, as discussed earlier in the [feature selection](#feature-selection) section. Using this condensed data format it is much easier to visualise a 'distance' between two army lists. We can imagine a flattened army list like a deck of cards, containing a card for each warscroll and enhancement. Then, if we want to compare two army lists, we can define our distance as the number of cards we need to add or remove from one to make it the same as the other.

To illustrate this, we'll work through a simplified example. Our first army list has 'cards' `[A, A, B, C]` and our second army list has `[A, C, D, E, F]`. Then we perform the following steps to transform the first list into the second:
- list 1: `[A, A, B, C]`,    list 2: `[A, C, D, E, F]` - initial lists;
- list 1: `[A, B, C]`,       list 2: `[A, C, D, E, F]` - remove extra `A`;
- list 1: `[A, C]`,          list 2: `[A, C, D, E, F]` - remove extra `B`;
- list 1: `[A, C, D, E, F]`, list 2: `[A, C, D, E, F]` - add missing `D`, `E` and `F`.

The total number of cards we added or removed was 5, so we would take the distance between the two army lists as 5.

A general metric for this type of distance is called the Levenshtein distance, and while it is usually applied to text strings, it is applicable to any similar sequence such as our decks of cards.

## Hyperparameter Tuning

Now we have reviewed the approach being taken by the classifier we can discuss the controls we have to fine tune its behaviour, and in which scenarios different values perform better or worse.

### Nearest Neighbours

First we can choose 'k', the number of neighbours that contribute to each classification. The default value for 'k' set by the tool is `1`, but any small positive integer can be a valid choice.

In many cases within a faction there may be up to 2 dominant archetypes, which means that an odd value for 'k' could be preferrable to avoid tied votes, however if there are commonly 3 or more archetypes within a faction this has no effect.

Additionally, the size and curation of the training data set affects which value of 'k' may be optimal. If the data set is large, or may contain mis-labelled entries (for example if every newly classified piece of data is added to the data set), a larger 'k' may be useful to average across data points. If the data set is small and correctly labelled, smaller 'k' may be preferred to avoid including distant neighbours.

### Classification Weight

On the topic of larger data sets, if one archetype is much more common than another it may dominate the data set, leading to the classifier mis-labelling data of the less common archetype. This is a common problem faced by this approach, but weighting neighbours' votes by their distance may be used to help overcome this issue.

In this tool, we use inverse distance weighting, i.e. `weight = 1/d`, when counting votes if this parameter is enabled. This gives closer neighbours a much stronger vote than further neighbours, meaning a single very close point can out-vote several further points, overcoming the problem of skewed archetype distributions.

As before, if the data set is small and curated such that there is no archetype dominance then this extra step would not be necessary. Alternatively, in some cases it may be desirable to have this biased classification, where a dominant archetype in the data set reflects the real world popularity of that archetype, and actually aids in classification.

### Warscroll and Enhancement Weights

As discussed in the [feature selection](#feature-selection) section, classification can be greatly hindered by the presence of irrelevant features which we have aimed to remove. While we are left with features we deem important, feature scaling is still required to adjust the relative importance of those remaining features.

The classifier has two parameters for controlling feature scaling: warscroll weight and enhancement weight, defaulting to `2` and `1` respectively. These are simple multipliers applied to the Levenshtein distance for each category. For example, if the distance between warscrolls for two army lists is `3`, and the distance between enhancements is `4`, the total weighted distance would be `(3 * 2) + (4 * 1) = 6 + 4 = 10`. We can see that despite the enhancement distance being greater, its total contribution (`4`) to the weighted distance (`10`) was smaller than the contribution of the higher weighted warscroll distance (`6`).

These weights are relative, so weights of `2` and `1` will have the same effect as `4` and `2` as the warscroll weight is still twice the enhancement weight in both cases. The weights should be adjusted heuristically based on the empirical importance of warscrolls versus enhancements when categorising army lists into archetypes.

## Knowledge Bank Curation

The final topic to cover is management of the training data set, which we otherwise refer to within the tool as the knowledge bank.

If newly classified data points are added to the data set, then it will continually grow. As discussed in the [lazy learning](#lazy-learning) section, larger data sets increase size and slow down performance, and class outliers or mis-labelled points can have negative effects on further classification, meaning that more data is not necessarily better.

For context, a class outlier is defined as a data point with one label, surrounded (in terms of the distance metric) by points with other labels. It may be itself mis-labelled, or it may be correctly labelled but overlapping with another class. In any case, data points like this can cause classification issues.

Data reduction algorithms exist, which seek to remove as much data as possible while maintaining classification accuracy, under the assumption that some minimal set of 'prototype' data points exist which can accurately classify new data, and any other points are either superfluous or harmful to classification.

In the context of this tool, given how accessible the data format is and how much prior knowledge is available, applying an algorithm to data reduction feels like extraneous effort. The initial knowledge bank will have to be constructed manually anyway, and it may make sense to simply create prototype data points in that step, then only ever modify the knowledge bank manually.

To explain with an example, suppose only two factions exist: `A` and `B`. Within faction `A` there are two army list archetypes being commonly played, `Foo` and `Bar`; and within faction `B` only one archetype exists, `Baz`. To start classifying army lists we first build our knowledge base, and to do so we pass in a prototypical version of `Foo`, `Bar` and `Baz` lists. When we classify new army lists that are variants of these archetypes, the prototype lists in our data set are always close enough that we get correct labels using `k = 1`. Later, a new army archetype `Qux` in faction `B` starts being played and our classifier mis-labels it as `Baz`. We can choose to add and correctly label the first `Qux` army list we see to our knowledge bank, then later manually modify it as we get a better idea of the prototypical version of `Qux`. Now suppose faction `A` gets an update and `Bar` stops being played - we may get new variants of `Foo` being mis-labelled as `Bar`, so we can choose to delete `Bar` from our knowledge bank.

Using this approach we still benefit from lazy learning's adaptability, but never have to worry about the problems associated with a large training data set.

## Closing Thoughts

The approach described here is unlikely to be perfect, and will require tuning and further iteration, and may ultimately be superseded by an alternative method. My primary goal is to encourage innovation and experimentation in this area for the benefit of everyone in the community, so I welcome new ideas, collaboration, criticism, and others to build upon and challenge the approaches discussed.

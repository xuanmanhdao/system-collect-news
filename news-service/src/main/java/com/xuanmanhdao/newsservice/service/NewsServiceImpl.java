package com.xuanmanhdao.newsservice.service;

import co.elastic.clients.elasticsearch.ElasticsearchClient;
import co.elastic.clients.elasticsearch.core.SearchRequest;
import co.elastic.clients.elasticsearch.core.SearchResponse;
import co.elastic.clients.elasticsearch.core.search.Hit;
import com.xuanmanhdao.newsservice.entity.NewsDocumentEntity;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;

import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
public class NewsServiceImpl implements NewsService {
    private final ElasticsearchClient elasticsearchClient;

    @Override
    public Iterable<NewsDocumentEntity> getAll() {
        try {
            SearchResponse<NewsDocumentEntity> response = elasticsearchClient.search(s -> s
                            .index("news")
                            .query(q -> q.matchAll(m -> m))
                            .size(1000),
                    NewsDocumentEntity.class);
            return response.hits().hits().stream().map(Hit::source).collect(Collectors.toList());
        } catch (Exception e) {
            log.error("❌ Lỗi khi truy vấn tất cả documents từ Elasticsearch", e);
            return Collections.emptyList();
        }
    }

    @Override
    public Page<NewsDocumentEntity> searchByTitle(String keyword, Pageable pageable) {
        try {
            SearchRequest request = SearchRequest.of(s -> s
                    .index("news")
                    .from((int) pageable.getOffset())
                    .size(pageable.getPageSize())
                    .query(q -> q.match(m -> m.field("title").query(keyword)))
            );

            return getNewsDocumentEntities(pageable, request);
        } catch (Exception e) {
            log.error("❌ Lỗi khi tìm kiếm theo title với keyword '{}'", keyword, e);
            return Page.empty();
        }
    }

    private Page<NewsDocumentEntity> getNewsDocumentEntities(Pageable pageable, SearchRequest request) throws java.io.IOException {
        SearchResponse<NewsDocumentEntity> response =
                elasticsearchClient.search(request, NewsDocumentEntity.class);

        List<NewsDocumentEntity> content = response.hits().hits()
                .stream()
                .map(Hit::source)
                .collect(Collectors.toList());

        long totalHits = response.hits().total() != null ? response.hits().total().value() : 0;

        return new PageImpl<>(content, pageable, totalHits);
    }

    @Override
    public Page<NewsDocumentEntity> searchBySource(String source, Pageable pageable) {
        try {
            SearchRequest request = SearchRequest.of(s -> s
                    .index("news")
                    .from((int) pageable.getOffset())
                    .size(pageable.getPageSize())
                    .query(q -> q.match(m -> m.field("source").query(source)))
            );

            return getNewsDocumentEntities(pageable, request);
        } catch (Exception e) {
            log.error("❌ Lỗi khi tìm kiếm theo source '{}'", source, e);
            return Page.empty();
        }
    }
}
